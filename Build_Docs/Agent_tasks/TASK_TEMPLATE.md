# Task Template

Future task specs should use this structure. Tasks are committed one at a time. After each task is complete, the next task's spec is re-evaluated against the evidence the completed task produced. The task series plan in `Build_Docs/Agent_tasks/Task_010_Series_Plan.md` is a target trajectory, not a commitment sequence. The primitive-sufficiency gate is the structural enforcement of Axiom 12 at task-commit time.

## Repository

State the repository path and the active clean-room warnings. Include V3 and V1 restrictions when relevant.

## Current Verified Baseline

List what is known to be complete at task start, including test counts and source-audit state when available.

## Task Goal

State what this task accomplishes in one narrow paragraph.

## Design Principles

List task-specific constraints and inherited architectural commitments.

## Primitive-Sufficiency Gate

Demonstrate that every concept the task requires is provided by parent layers. If not, list the prior parent-extension tasks required before this task can proceed.

## Required Deliverables

List specific files, modules, statuses, protocols, transition rules, reports, or documents.

## Required Tests

List required test files and one-sentence descriptions of what each verifies.

## Required Commands

List commands for the red slice, green slice, full suite, and source audits.

## Non-Goals

List what this task explicitly does not do.

## Completion Report

Specify the report directory and required report contents.

## Acceptance Criteria

Provide a numbered list of concrete conditions for task completion.
