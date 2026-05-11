from lloyd_v4.projection import BranchSelection, branch_selection, exact_quadratic_projection


def project_with_branch(root_state_result, branch: str | BranchSelection):
    selected = branch if isinstance(branch, BranchSelection) else BranchSelection(branch)
    return exact_quadratic_projection(root_state_result, branch_selection(selected))
