"""
=============================================================================
STP Headless Validator — Academic Audit Mode
=============================================================================
Bypass the PyQt6 UI entirely. Loads `constrained.json`, runs the full
GRASP → SA pipeline, then executes explicit mathematical assertions against
H1–H4 (hard constraints) and profiles S1–S2 (soft constraints).

Output Mode  : Diagnostic Profiler + Hard Constraint Assertions
Logging Lib  : rich (install via: pip install rich)
Dataset      : constrained.json (50 professors, 30 classes, 25 periods)
SA Runs      : 1 (single, deterministic, ~30s runtime)

Run Command  :
    cd /home/anybody/Documents/Projects/timetable-solution-metaheuristic
    source .venv/bin/activate && pip install rich
    python -m tests.headless_validator

Exit Code:
    0 — All H1–H4 hard constraints satisfied
    1 — One or more hard constraint violations remain in the final matrix
=============================================================================
"""

import sys
import os
import json
import time
from collections import Counter
from typing import Dict, List, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# PATH SETUP — ensure project root is on sys.path regardless of invocation
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# RICH IMPORTS (fail fast with a clear message if not installed)
# ---------------------------------------------------------------------------
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.text import Text
    from rich import box
except ImportError:
    print("\n[ERROR] The 'rich' library is not installed.")
    print("Fix: pip install rich\n")
    sys.exit(1)

# ---------------------------------------------------------------------------
# STP ENGINE IMPORTS
# ---------------------------------------------------------------------------
from src.models.stp_state import STPState
from src.core.state import TimetableState
from src.core.evaluator import STPEvaluator
from src.engine.grasp import GRASPEngine
from src.engine.sa_optimizer import SimulatedAnnealingEngine

# ---------------------------------------------------------------------------
# GLOBALS
# ---------------------------------------------------------------------------
console = Console()
DATASET_PATH = os.path.join(PROJECT_ROOT, "constrained.json")


# ===========================================================================
# SECTION 1: DATA LOADING
# ===========================================================================

def load_dataset(path: str) -> STPState:
    """Load the JSON dataset and return a validated STPState model."""
    if not os.path.exists(path):
        console.print(f"[bold red][FATAL] Dataset not found: {path}[/bold red]")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # Validate JSON schema using Pydantic
    try:
        stp = STPState(**raw)
    except Exception as e:
        console.print(f"[bold red][FATAL] Invalid dataset schema: {e}[/bold red]")
        sys.exit(1)

    return stp


# ===========================================================================
# SECTION 2: MATHEMATICAL ASSERTION FUNCTIONS
# ===========================================================================

def assert_h1_no_clashes(matrix: np.ndarray, int_to_class_disc: Dict) -> Tuple[int, List[str]]:
    """
    H1 — Class Clash Verification.
    Asserts: For every column j in [0, P), no class (turma) appears
    in more than one row simultaneously.

    Returns:
        (clash_count, details): Total number of excess clash occurrences
        and a list of human-readable descriptions of each violation.
    """
    total_clashes = 0
    details = []

    for col in range(matrix.shape[1]):
        turma_map: Dict[str, List[int]] = {}
        for row in range(matrix.shape[0]):
            val = matrix[row, col]
            if val > 0:
                turma_id = int_to_class_disc[val][0]
                turma_map.setdefault(turma_id, []).append(row)

        for turma_id, rows in turma_map.items():
            if len(rows) > 1:
                excess = len(rows) - 1
                total_clashes += excess
                details.append(
                    f"Period {col + 1} (col={col}): Turma '{turma_id}' "
                    f"clashes across {len(rows)} professors (rows: {rows})"
                )

    return total_clashes, details


def assert_h2_no_unavailability_overwrite(
    matrix: np.ndarray,
    stp: STPState,
    prof_id_to_idx: Dict[str, int]
) -> Tuple[int, List[str]]:
    """
    H2 — Unavailability Sentinel Integrity.
    Asserts: For every slot declared as 'indisponivel' in the JSON,
    the matrix cell must still contain -1.

    Returns:
        (violation_count, details)
    """
    violations = 0
    details = []

    for prof in stp.professores:
        if prof.id_professor not in prof_id_to_idx:
            continue
        row_idx = prof_id_to_idx[prof.id_professor]
        for slot_1based in prof.indisponibilidades:
            col_idx = slot_1based - 1
            if 0 <= col_idx < matrix.shape[1]:
                val = matrix[row_idx, col_idx]
                if val != -1:
                    violations += 1
                    details.append(
                        f"Prof '{prof.id_professor}' (row={row_idx}): "
                        f"Slot {slot_1based} (col={col_idx}) should be -1, found {val}"
                    )

    return violations, details


def assert_h3_workload_limits(
    matrix: np.ndarray,
    stp: STPState,
    prof_id_to_idx: Dict[str, int]
) -> Tuple[int, List[str]]:
    """
    H3 — Maximum Workload Verification.
    Asserts: The number of active slots (value > 0) in professor row i
    must not exceed that professor's declared carga_maxima.

    Returns:
        (violation_count, details)
    """
    violations = 0
    details = []

    for prof in stp.professores:
        if prof.id_professor not in prof_id_to_idx:
            continue
        row_idx = prof_id_to_idx[prof.id_professor]
        actual_load = int(np.sum(matrix[row_idx] > 0))
        if actual_load > prof.carga_maxima:
            violations += 1
            excess = actual_load - prof.carga_maxima
            details.append(
                f"Prof '{prof.id_professor}' (row={row_idx}): "
                f"Allocated {actual_load} slots > carga_maxima={prof.carga_maxima} "
                f"(excess: +{excess})"
            )

    return violations, details


def assert_h4_curriculum_integrity(
    matrix: np.ndarray,
    stp: STPState,
    prof_id_to_idx: Dict[str, int],
    class_disc_to_int: Dict
) -> Tuple[int, List[str]]:
    """
    H4 — Curriculum Completeness Verification (THE CRITICAL GAP).
    Asserts: For every demand (id_professor, id_turma, id_disciplina, quantidade_aulas),
    exactly `quantidade_aulas` cells in the professor's row must contain
    the integer code for (id_turma, id_disciplina).

    This assertion is ABSENT from the production codebase and is the
    primary new assertion contributed by this validator.

    Returns:
        (violation_count, details)
    """
    violations = 0
    details = []

    for demanda in stp.demandas:
        prof_id = demanda.id_professor
        if prof_id not in prof_id_to_idx:
            # Professor in demands but not in matrix — data integrity error
            violations += 1
            details.append(
                f"MISSING PROFESSOR: '{prof_id}' is referenced in demands "
                f"but has no row in the matrix."
            )
            continue

        row_idx = prof_id_to_idx[prof_id]
        key = (demanda.id_turma, demanda.id_disciplina)

        if key not in class_disc_to_int:
            # Encoding map gap — demand was never registered
            violations += 1
            details.append(
                f"Prof '{prof_id}', Demand (Turma={demanda.id_turma}, "
                f"Disc={demanda.id_disciplina}): No encoding found in class_disc_to_int map. "
                f"This lesson was never registered by GRASP."
            )
            continue

        code = class_disc_to_int[key]
        actual_count = int(np.sum(matrix[row_idx] == code))
        expected_count = demanda.quantidade_aulas

        if actual_count != expected_count:
            violations += 1
            diff = actual_count - expected_count
            direction = f"+{diff}" if diff > 0 else str(diff)
            details.append(
                f"Prof '{prof_id}', Turma={demanda.id_turma}, Disc={demanda.id_disciplina}: "
                f"Expected {expected_count} slots, found {actual_count} ({direction})"
            )

    return violations, details


# ===========================================================================
# SECTION 3: SOFT CONSTRAINT PROFILERS (S1, S2)
# ===========================================================================

def profile_s1_windows(matrix: np.ndarray, periodos_por_dia: int) -> Dict:
    """S1 — Window profiler: per-professor and total window counts."""
    per_prof = {}
    dias = matrix.shape[1] // periodos_por_dia
    for row in range(matrix.shape[0]):
        total_janelas = 0
        for d in range(dias):
            inicio = d * periodos_por_dia
            fim = inicio + periodos_por_dia
            dia_aulas = matrix[row, inicio:fim]
            idx_com_aula = np.where(dia_aulas > 0)[0]
            if len(idx_com_aula) > 1:
                primeiro = idx_com_aula[0]
                ultimo = idx_com_aula[-1]
                buracos = int(np.sum(dia_aulas[primeiro:ultimo + 1] <= 0))
                total_janelas += buracos
        per_prof[row] = total_janelas
    return per_prof


def profile_s2_days(matrix: np.ndarray, periodos_por_dia: int) -> Dict:
    """S2 — Commuting day profiler: per-professor and total day counts."""
    per_prof = {}
    dias = matrix.shape[1] // periodos_por_dia
    for row in range(matrix.shape[0]):
        dias_usados = 0
        for d in range(dias):
            inicio = d * periodos_por_dia
            fim = inicio + periodos_por_dia
            if np.any(matrix[row, inicio:fim] > 0):
                dias_usados += 1
        per_prof[row] = dias_usados
    return per_prof


# ===========================================================================
# SECTION 4: REPORTING UTILITIES
# ===========================================================================

def print_banner():
    banner_text = Text(
        "STP Headless Validator — Academic Audit Mode", style="bold white"
    )
    subtitle = Text(
        "GRASP + Simulated Annealing — Constraint Verification Pipeline",
        style="dim"
    )
    console.print(Panel.fit(
        f"{banner_text}\n{subtitle}",
        border_style="bright_blue",
        padding=(1, 4),
    ))
    console.print()


def print_pre_optimization_snapshot(
    matrix: np.ndarray,
    int_to_class_disc: Dict,
    stp: STPState,
    periodos: int,
    label: str = "PRE-OPTIMIZATION"
):
    """Prints a snapshot of all constraint counts before/after optimization."""
    clashes = STPEvaluator.evaluate_clashes(matrix, int_to_class_disc)
    windows = STPEvaluator.evaluate_windows(matrix, periodos)
    days = STPEvaluator.evaluate_days(matrix, periodos)

    console.print(f"[bold cyan]── {label} SNAPSHOT ──[/bold cyan]")
    t = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    t.add_column("Metric", style="bold")
    t.add_column("Value", justify="right")
    t.add_row("H1 Class Clashes (C)", str(clashes),)
    t.add_row("S1 Total Windows (J)", str(windows))
    t.add_row("S2 Total Commuting Days (D)", str(days))
    total_cost = (
        stp.parametros_execucao.pesos_objetivo.alpha * windows
        + stp.parametros_execucao.pesos_objetivo.beta * days
        + stp.parametros_execucao.pesos_objetivo.gamma * clashes
    )
    t.add_row("f(X) Total Cost", f"{total_cost:.2f}", style="bold yellow")
    console.print(t)
    console.print()

    return clashes, windows, days


def print_comparison_table(
    pre: Tuple, post: Tuple,
    alpha: float, beta: float, gamma: float
):
    """Prints a before/after comparison table for all constraint metrics."""
    pre_clashes, pre_windows, pre_days = pre
    post_clashes, post_windows, post_days = post

    pre_cost = alpha * pre_windows + beta * pre_days + gamma * pre_clashes
    post_cost = alpha * post_windows + beta * post_days + gamma * post_clashes

    def delta_str(before, after):
        diff = after - before
        if diff < 0:
            return f"[green]↓ {abs(diff)}[/green]"
        elif diff > 0:
            return f"[red]↑ {diff}[/red]"
        else:
            return "[dim]= 0[/dim]"

    t = Table(
        title="Before vs. After Optimization",
        box=box.DOUBLE_EDGE,
        show_header=True,
        header_style="bold white on dark_blue"
    )
    t.add_column("Constraint / Metric", style="bold", min_width=30)
    t.add_column("Pre-GRASP", justify="center", style="yellow")
    t.add_column("Post-SA", justify="center", style="cyan")
    t.add_column("Delta", justify="center")

    t.add_row("H1 — Class Clashes (×γ)", str(pre_clashes), str(post_clashes), delta_str(pre_clashes, post_clashes))
    t.add_row("S1 — Windows (×α)", str(pre_windows), str(post_windows), delta_str(pre_windows, post_windows))
    t.add_row("S2 — Commuting Days (×β)", str(pre_days), str(post_days), delta_str(pre_days, post_days))
    t.add_row(
        "f(X) — Total Cost",
        f"{pre_cost:.2f}",
        f"{post_cost:.2f}",
        delta_str(pre_cost, post_cost)
    )

    console.print(t)
    console.print()


def print_assertion_results(
    h1_result: Tuple, h2_result: Tuple, h3_result: Tuple, h4_result: Tuple,
    verbose: bool = True
) -> bool:
    """
    Prints per-constraint assertion results.
    Returns True if all hard constraints are satisfied.
    """
    h1_count, h1_details = h1_result
    h2_count, h2_details = h2_result
    h3_count, h3_details = h3_result
    h4_count, h4_details = h4_result

    all_passed = (h1_count == 0 and h2_count == 0 and h3_count == 0 and h4_count == 0)

    t = Table(
        title="Hard Constraint Assertion Report (H1–H4)",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white"
    )
    t.add_column("Constraint", style="bold", min_width=40)
    t.add_column("Violations", justify="center")
    t.add_column("Status", justify="center")

    def status(count):
        return "[bold green]✅ PASS[/bold green]" if count == 0 else "[bold red]❌ FAIL[/bold red]"

    t.add_row("H1 — Class Clashes (No turma simultaneously in 2+ teachers)", str(h1_count), status(h1_count))
    t.add_row("H2 — Unavailability Sentinels (-1 cells never overwritten)", str(h2_count), status(h2_count))
    t.add_row("H3 — Workload Limits (Alloc ≤ carga_maxima per professor)", str(h3_count), status(h3_count))
    t.add_row("H4 — Curriculum Integrity (Demand quantity matches final matrix)", str(h4_count), status(h4_count))

    console.print(t)
    console.print()

    # Print violation details if any
    if verbose:
        if h1_count > 0:
            console.print(Panel(
                "\n".join(h1_details[:20]),  # Cap at 20 to avoid floods
                title="[red]H1 Violation Details[/red]",
                border_style="red"
            ))
        if h2_count > 0:
            console.print(Panel(
                "\n".join(h2_details),
                title="[red]H2 Violation Details[/red]",
                border_style="red"
            ))
        if h3_count > 0:
            console.print(Panel(
                "\n".join(h3_details),
                title="[red]H3 Violation Details[/red]",
                border_style="red"
            ))
        if h4_count > 0:
            console.print(Panel(
                "\n".join(h4_details[:30]),  # Cap at 30
                title="[red]H4 Violation Details[/red]",
                border_style="red"
            ))

    return all_passed


def print_per_professor_soft_profile(
    matrix: np.ndarray,
    stp: STPState,
    prof_id_to_idx: Dict[str, int],
    periodos: int,
    top_n: int = 10
):
    """Prints the top N professors with the most windows (S1 bottleneck scan)."""
    s1_profile = profile_s1_windows(matrix, periodos)
    s2_profile = profile_s2_days(matrix, periodos)

    idx_to_prof = {v: k for k, v in prof_id_to_idx.items()}

    # Sort by windows descending
    sorted_by_windows = sorted(s1_profile.items(), key=lambda x: x[1], reverse=True)

    t = Table(
        title=f"Top-{top_n} Professors by Residual Window Count (S1 Bottlenecks)",
        box=box.SIMPLE_HEAD,
        header_style="bold magenta"
    )
    t.add_column("Professor ID", style="bold")
    t.add_column("Windows (J)", justify="right", style="yellow")
    t.add_column("Commuting Days (D)", justify="right", style="cyan")
    t.add_column("Active Slots", justify="right")

    for row_idx, janelas in sorted_by_windows[:top_n]:
        prof_id = idx_to_prof.get(row_idx, f"row_{row_idx}")
        dias = s2_profile.get(row_idx, 0)
        active = int(np.sum(matrix[row_idx] > 0))
        t.add_row(prof_id, str(janelas), str(dias), str(active))

    console.print(t)
    console.print()


# ===========================================================================
# SECTION 5: MAIN VALIDATION PIPELINE
# ===========================================================================

def main():
    print_banner()
    start_time = time.time()

    # ------------------------------------------------------------------
    # STEP 1: Load Dataset
    # ------------------------------------------------------------------
    console.print("[bold]Step 1/5:[/bold] Loading dataset...", end=" ")
    stp = load_dataset(DATASET_PATH)
    periodos = stp.parametros_execucao.periodos_por_dia
    dias = stp.parametros_execucao.dias_letivos
    n_profs = len(stp.professores)
    n_turmas = len(stp.turmas)
    n_demands = len(stp.demandas)
    total_aulas = sum(d.quantidade_aulas for d in stp.demandas)

    console.print(f"[green]OK[/green]")
    console.print(Panel(
        f"Professors: [bold]{n_profs}[/bold]  |  "
        f"Classes (Turmas): [bold]{n_turmas}[/bold]  |  "
        f"Demands: [bold]{n_demands}[/bold]  |  "
        f"Total Lessons to Allocate: [bold]{total_aulas}[/bold]\n"
        f"Matrix Dimensions: [bold]{n_profs} × {periodos * dias}[/bold]  "
        f"({dias} days × {periodos} periods/day)",
        title="Dataset Overview",
        border_style="dim"
    ))

    # ------------------------------------------------------------------
    # STEP 2: Initialize Timetable State (Pre-GRASP)
    # ------------------------------------------------------------------
    console.print("[bold]Step 2/5:[/bold] Initializing TimetableState...")
    state = TimetableState(stp)
    matrix = state.matrix

    # Capture pre-optimization snapshot (matrix is empty with -1 sentinels)
    pre_clashes, pre_windows, pre_days = print_pre_optimization_snapshot(
        matrix, state.int_to_class_disc, stp, periodos, "PRE-OPTIMIZATION (Empty Matrix)"
    )

    # ------------------------------------------------------------------
    # STEP 3: Run GRASP Construction
    # ------------------------------------------------------------------
    console.print("[bold]Step 3/5:[/bold] Running GRASP construction phase...")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("GRASP: Building initial solution...", total=None)
        grasp_start = time.time()
        grasp_engine = GRASPEngine(state, recorder=None)
        grasp_engine.build_initial_solution()
        grasp_elapsed = time.time() - grasp_start
        progress.update(task, description=f"GRASP: Done in {grasp_elapsed:.2f}s")

    console.print(f"  GRASP completed in [bold]{grasp_elapsed:.2f}s[/bold]")
    post_grasp_clashes = STPEvaluator.evaluate_clashes(matrix, state.int_to_class_disc)
    post_grasp_windows = STPEvaluator.evaluate_windows(matrix, periodos)
    post_grasp_days = STPEvaluator.evaluate_days(matrix, periodos)
    console.print(
        f"  Post-GRASP: [yellow]H1 Clashes={post_grasp_clashes}[/yellow], "
        f"S1 Windows={post_grasp_windows}, "
        f"S2 Days={post_grasp_days}"
    )
    console.print()

    # ------------------------------------------------------------------
    # STEP 4: Run Simulated Annealing Refinement
    # ------------------------------------------------------------------
    console.print("[bold]Step 4/5:[/bold] Running Simulated Annealing refinement phase...")
    sa_params = stp.parametros_execucao.sa_parametros
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task(
            f"SA: T₀={sa_params.temperatura_inicial}, "
            f"α={sa_params.taxa_resfriamento}, "
            f"T_min={sa_params.temperatura_minima}",
            total=None
        )
        sa_start = time.time()
        sa_engine = SimulatedAnnealingEngine(
            state,
            recorder=None,
            t_initial=sa_params.temperatura_inicial,
            t_final=sa_params.temperatura_minima,
            alpha_cooling=sa_params.taxa_resfriamento,
            iter_per_temp=sa_params.iteracoes_por_temperatura
        )
        sa_engine.run()
        sa_elapsed = time.time() - sa_start
        progress.update(task, description=f"SA: Done in {sa_elapsed:.2f}s")

    console.print(f"  SA completed in [bold]{sa_elapsed:.2f}s[/bold]")
    console.print()

    # ------------------------------------------------------------------
    # STEP 5: Mathematical Assertions
    # ------------------------------------------------------------------
    console.print("[bold]Step 5/5:[/bold] Executing mathematical assertions...\n")

    # Post-SA metrics for comparison table
    post_sa_clashes = STPEvaluator.evaluate_clashes(matrix, state.int_to_class_disc)
    post_sa_windows = STPEvaluator.evaluate_windows(matrix, periodos)
    post_sa_days = STPEvaluator.evaluate_days(matrix, periodos)

    # Before/After comparison table
    print_comparison_table(
        pre=(post_grasp_clashes, post_grasp_windows, post_grasp_days),
        post=(post_sa_clashes, post_sa_windows, post_sa_days),
        alpha=stp.parametros_execucao.pesos_objetivo.alpha,
        beta=stp.parametros_execucao.pesos_objetivo.beta,
        gamma=stp.parametros_execucao.pesos_objetivo.gamma,
    )

    # Run all four hard constraint assertions
    h1_result = assert_h1_no_clashes(matrix, state.int_to_class_disc)
    h2_result = assert_h2_no_unavailability_overwrite(matrix, stp, state.prof_id_to_idx)
    h3_result = assert_h3_workload_limits(matrix, stp, state.prof_id_to_idx)
    h4_result = assert_h4_curriculum_integrity(
        matrix, stp, state.prof_id_to_idx, state.class_disc_to_int
    )

    all_passed = print_assertion_results(h1_result, h2_result, h3_result, h4_result)

    # Soft constraint profiler (S1 bottleneck scan)
    print_per_professor_soft_profile(matrix, stp, state.prof_id_to_idx, periodos, top_n=10)

    # ------------------------------------------------------------------
    # FINAL VERDICT
    # ------------------------------------------------------------------
    total_elapsed = time.time() - start_time
    console.print(f"[dim]Total validation time: {total_elapsed:.2f}s[/dim]")
    console.print()

    if all_passed:
        console.print(Panel(
            "[bold green]✅ ALL HARD CONSTRAINTS SATISFIED (H1–H4)[/bold green]\n\n"
            "The optimized timetable matrix is mathematically feasible.\n"
            "The implementation correctly enforces all hard constraints defined\n"
            "in the Souza et al. / Zhang et al. hybrid model.",
            title="[bold green]VALIDATION RESULT: PASS[/bold green]",
            border_style="green",
            padding=(1, 4)
        ))
        sys.exit(0)
    else:
        total_violations = (
            h1_result[0] + h2_result[0] + h3_result[0] + h4_result[0]
        )
        console.print(Panel(
            f"[bold red]❌ HARD CONSTRAINT VIOLATIONS DETECTED: {total_violations} total[/bold red]\n\n"
            "One or more hard constraints (H1–H4) remain violated in the final matrix.\n"
            "Review the violation details above to identify the root cause.\n\n"
            "[yellow]Common Causes:[/yellow]\n"
            "  • H1: SA temperature too low / iterations insufficient to eliminate all clashes\n"
            "  • H4: GRASP silent-drop (no candidates) for over-constrained professors\n"
            "  • H3: Data-entry bypass — possible if dataset was modified outside the UI\n"
            "  • H2: Constructor bug — should never happen; if raised, it is a critical bug",
            title="[bold red]VALIDATION RESULT: FAIL[/bold red]",
            border_style="red",
            padding=(1, 4)
        ))
        sys.exit(1)


# ===========================================================================
# ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    main()
