"""
Coordination Utilities for Massive Admin Testing Operation
Provides shared utilities for multi-squad coordination, dependency management,
and conflict resolution during the massive testing operation.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid


class SquadStatus(Enum):
    """Squad status enumeration."""
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class ConflictPriority(Enum):
    """Conflict priority levels."""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class SquadProgress:
    """Progress tracking for a squad."""
    squad_id: str
    coverage_percentage: float
    tests_created: int
    tests_passing: int
    tests_failing: int
    security_tests: int
    performance_benchmarks: int
    last_update: str
    status: SquadStatus
    blockers: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class DependencyRequest:
    """Dependency request between squads."""
    request_id: str
    from_squad: str
    to_squad: str
    resource: str
    description: str
    timestamp: str
    status: str = "PENDING"
    priority: str = "NORMAL"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class ConflictReport:
    """Conflict report between squads."""
    conflict_id: str
    squad_a: str
    squad_b: str
    conflict_type: str
    description: str
    priority: ConflictPriority
    timestamp: str
    status: str = "ACTIVE"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class CoordinationUtils:
    """Utilities for multi-squad coordination."""

    def __init__(self, workspace_path: str = ".workspace"):
        self.workspace_path = Path(workspace_path)
        self.coordination_file = self.workspace_path / "communications" / "coordination-channel.json"
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for coordination utilities."""
        logger = logging.getLogger("coordination_utils")
        logger.setLevel(logging.INFO)

        # Create handler if not exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def load_coordination_data(self) -> Dict:
        """Load coordination data from JSON file."""
        try:
            with open(self.coordination_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Coordination file not found: {self.coordination_file}")
            return self._create_default_coordination_data()
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing coordination data: {e}")
            return self._create_default_coordination_data()

    def save_coordination_data(self, data: Dict) -> bool:
        """Save coordination data to JSON file."""
        try:
            # Ensure directory exists
            self.coordination_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.coordination_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving coordination data: {e}")
            return False

    def _create_default_coordination_data(self) -> Dict:
        """Create default coordination data structure."""
        return {
            "operation_id": "MASSIVE_ADMIN_TESTING_2025_09_21",
            "status": "INITIALIZING",
            "squads": {},
            "dependencies": [],
            "conflicts": [],
            "checkpoints": {},
            "quality_gates": {},
            "communication_log": []
        }

    def register_squad_progress(self, progress: SquadProgress) -> bool:
        """Register progress for a squad."""
        try:
            data = self.load_coordination_data()

            # Update squad progress
            squad_data = progress.to_dict()
            squad_data['status'] = squad_data['status'].value if isinstance(squad_data['status'], SquadStatus) else squad_data['status']

            if 'squads' not in data:
                data['squads'] = {}

            data['squads'][progress.squad_id] = squad_data

            # Add to communication log
            self._add_communication_log(
                data,
                progress.squad_id,
                "PROGRESS_UPDATE",
                f"Coverage: {progress.coverage_percentage}%, Tests: {progress.tests_created}"
            )

            success = self.save_coordination_data(data)
            if success:
                self.logger.info(f"Progress registered for {progress.squad_id}: {progress.coverage_percentage}%")

            return success

        except Exception as e:
            self.logger.error(f"Error registering squad progress: {e}")
            return False

    def request_dependency(self, from_squad: str, to_squad: str, resource: str,
                          description: str = "", priority: str = "NORMAL") -> Optional[str]:
        """Request a dependency between squads."""
        try:
            request_id = str(uuid.uuid4())[:8]
            timestamp = datetime.utcnow().isoformat() + 'Z'

            dependency = DependencyRequest(
                request_id=request_id,
                from_squad=from_squad,
                to_squad=to_squad,
                resource=resource,
                description=description,
                timestamp=timestamp,
                priority=priority
            )

            data = self.load_coordination_data()

            if 'dependencies' not in data:
                data['dependencies'] = []

            data['dependencies'].append(dependency.to_dict())

            # Add to communication log
            self._add_communication_log(
                data,
                from_squad,
                "DEPENDENCY_REQUEST",
                f"Requesting '{resource}' from {to_squad}"
            )

            success = self.save_coordination_data(data)
            if success:
                self.logger.info(f"Dependency requested: {from_squad} -> {to_squad} ({resource})")

            return request_id if success else None

        except Exception as e:
            self.logger.error(f"Error requesting dependency: {e}")
            return None

    def resolve_dependency(self, request_id: str, resolution: str) -> bool:
        """Resolve a dependency request."""
        try:
            data = self.load_coordination_data()
            dependencies = data.get('dependencies', [])

            for dep in dependencies:
                if dep.get('request_id') == request_id:
                    dep['status'] = 'RESOLVED'
                    dep['resolution'] = resolution
                    dep['resolved_at'] = datetime.utcnow().isoformat() + 'Z'

                    # Add to communication log
                    self._add_communication_log(
                        data,
                        dep['to_squad'],
                        "DEPENDENCY_RESOLVED",
                        f"Resolved dependency for {dep['from_squad']}: {resolution}"
                    )

                    success = self.save_coordination_data(data)
                    if success:
                        self.logger.info(f"Dependency resolved: {request_id}")

                    return success

            self.logger.warning(f"Dependency request not found: {request_id}")
            return False

        except Exception as e:
            self.logger.error(f"Error resolving dependency: {e}")
            return False

    def report_conflict(self, squad_a: str, squad_b: str, conflict_type: str,
                       description: str, priority: ConflictPriority = ConflictPriority.NORMAL) -> Optional[str]:
        """Report a conflict between squads."""
        try:
            conflict_id = str(uuid.uuid4())[:8]
            timestamp = datetime.utcnow().isoformat() + 'Z'

            conflict = ConflictReport(
                conflict_id=conflict_id,
                squad_a=squad_a,
                squad_b=squad_b,
                conflict_type=conflict_type,
                description=description,
                priority=priority,
                timestamp=timestamp
            )

            data = self.load_coordination_data()

            if 'conflicts' not in data:
                data['conflicts'] = []

            conflict_dict = conflict.to_dict()
            conflict_dict['priority'] = conflict_dict['priority'].value if isinstance(conflict_dict['priority'], ConflictPriority) else conflict_dict['priority']

            data['conflicts'].append(conflict_dict)

            # Add to communication log with appropriate priority
            log_priority = "CRITICAL" if priority == ConflictPriority.CRITICAL else "HIGH"
            self._add_communication_log(
                data,
                "coordination-system",
                "CONFLICT_REPORTED",
                f"Conflict between {squad_a} and {squad_b}: {description}",
                log_priority
            )

            success = self.save_coordination_data(data)
            if success:
                self.logger.warning(f"Conflict reported: {squad_a} vs {squad_b} ({conflict_type})")

            return conflict_id if success else None

        except Exception as e:
            self.logger.error(f"Error reporting conflict: {e}")
            return None

    def resolve_conflict(self, conflict_id: str, resolution: str, resolver: str = "communication-hub-ai") -> bool:
        """Resolve a conflict."""
        try:
            data = self.load_coordination_data()
            conflicts = data.get('conflicts', [])

            for conflict in conflicts:
                if conflict.get('conflict_id') == conflict_id:
                    conflict['status'] = 'RESOLVED'
                    conflict['resolution'] = resolution
                    conflict['resolver'] = resolver
                    conflict['resolved_at'] = datetime.utcnow().isoformat() + 'Z'

                    # Add to communication log
                    self._add_communication_log(
                        data,
                        resolver,
                        "CONFLICT_RESOLVED",
                        f"Resolved conflict {conflict_id}: {resolution}"
                    )

                    success = self.save_coordination_data(data)
                    if success:
                        self.logger.info(f"Conflict resolved: {conflict_id} by {resolver}")

                    return success

            self.logger.warning(f"Conflict not found: {conflict_id}")
            return False

        except Exception as e:
            self.logger.error(f"Error resolving conflict: {e}")
            return False

    def check_squad_dependencies(self, squad_id: str) -> List[Dict]:
        """Check pending dependencies for a squad."""
        try:
            data = self.load_coordination_data()
            dependencies = data.get('dependencies', [])

            pending_deps = [
                dep for dep in dependencies
                if dep.get('from_squad') == squad_id and dep.get('status') == 'PENDING'
            ]

            return pending_deps

        except Exception as e:
            self.logger.error(f"Error checking dependencies for {squad_id}: {e}")
            return []

    def get_squad_status(self, squad_id: str) -> Optional[Dict]:
        """Get current status of a squad."""
        try:
            data = self.load_coordination_data()
            squads = data.get('squads', {})

            return squads.get(squad_id)

        except Exception as e:
            self.logger.error(f"Error getting squad status for {squad_id}: {e}")
            return None

    def get_active_conflicts(self, squad_id: Optional[str] = None) -> List[Dict]:
        """Get active conflicts, optionally filtered by squad."""
        try:
            data = self.load_coordination_data()
            conflicts = data.get('conflicts', [])

            active_conflicts = [
                conflict for conflict in conflicts
                if conflict.get('status') == 'ACTIVE'
            ]

            if squad_id:
                active_conflicts = [
                    conflict for conflict in active_conflicts
                    if conflict.get('squad_a') == squad_id or conflict.get('squad_b') == squad_id
                ]

            return active_conflicts

        except Exception as e:
            self.logger.error(f"Error getting active conflicts: {e}")
            return []

    def calculate_overall_progress(self) -> Dict:
        """Calculate overall operation progress."""
        try:
            data = self.load_coordination_data()
            squads = data.get('squads', {})

            if not squads:
                return {"overall_progress": 0, "squad_count": 0}

            total_coverage = sum(
                squad.get('coverage_percentage', 0)
                for squad in squads.values()
            )

            avg_coverage = total_coverage / len(squads)

            total_tests = sum(
                squad.get('tests_created', 0)
                for squad in squads.values()
            )

            passing_tests = sum(
                squad.get('tests_passing', 0)
                for squad in squads.values()
            )

            return {
                "overall_progress": round(avg_coverage, 2),
                "squad_count": len(squads),
                "total_tests": total_tests,
                "passing_tests": passing_tests,
                "test_pass_rate": round((passing_tests / total_tests * 100) if total_tests > 0 else 0, 2)
            }

        except Exception as e:
            self.logger.error(f"Error calculating overall progress: {e}")
            return {"overall_progress": 0, "squad_count": 0}

    def validate_checkpoint(self, checkpoint_name: str) -> Dict:
        """Validate a checkpoint across all squads."""
        try:
            data = self.load_coordination_data()
            squads = data.get('squads', {})
            checkpoints = data.get('checkpoints', {})

            if checkpoint_name not in checkpoints:
                return {"status": "NOT_FOUND", "message": f"Checkpoint {checkpoint_name} not found"}

            checkpoint = checkpoints[checkpoint_name]
            criteria = checkpoint.get('criteria', [])

            # Evaluate criteria
            results = {}
            all_passed = True

            for criterion in criteria:
                passed = self._evaluate_checkpoint_criterion(criterion, squads)
                results[criterion] = passed
                if not passed:
                    all_passed = False

            # Update checkpoint status
            checkpoint['status'] = 'PASSED' if all_passed else 'FAILED'
            checkpoint['validated_at'] = datetime.utcnow().isoformat() + 'Z'
            checkpoint['results'] = results

            # Save updated data
            self.save_coordination_data(data)

            self.logger.info(f"Checkpoint {checkpoint_name} {'PASSED' if all_passed else 'FAILED'}")

            return {
                "status": checkpoint['status'],
                "results": results,
                "message": f"Checkpoint {checkpoint_name} {'passed' if all_passed else 'failed'}"
            }

        except Exception as e:
            self.logger.error(f"Error validating checkpoint {checkpoint_name}: {e}")
            return {"status": "ERROR", "message": str(e)}

    def _evaluate_checkpoint_criterion(self, criterion: str, squads: Dict) -> bool:
        """Evaluate a specific checkpoint criterion."""
        criterion_lower = criterion.lower()

        if "squads activated" in criterion_lower:
            return all(
                squad.get('status') not in ['INITIALIZING', 'ERROR']
                for squad in squads.values()
            )
        elif "fixtures created" in criterion_lower:
            return all(
                squad.get('tests_created', 0) > 0
                for squad in squads.values()
            )
        elif "red tests" in criterion_lower:
            return all(
                squad.get('coverage_percentage', 0) >= 50
                for squad in squads.values()
            )
        elif "green tests" in criterion_lower:
            return all(
                squad.get('coverage_percentage', 0) >= 80
                for squad in squads.values()
            )
        elif "integration" in criterion_lower:
            return all(
                squad.get('coverage_percentage', 0) >= 90
                for squad in squads.values()
            )
        elif "coverage" in criterion_lower:
            overall = self.calculate_overall_progress()
            return overall.get('overall_progress', 0) >= 95
        else:
            # Default: check if all squads are active
            return all(
                squad.get('status') == 'ACTIVE'
                for squad in squads.values()
            )

    def _add_communication_log(self, data: Dict, agent: str, message_type: str,
                              message: str, priority: str = "NORMAL"):
        """Add entry to communication log."""
        if 'communication_log' not in data:
            data['communication_log'] = []

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "agent": agent,
            "type": message_type,
            "message": message,
            "priority": priority
        }

        data['communication_log'].append(log_entry)

        # Keep only last 100 log entries to prevent file bloat
        if len(data['communication_log']) > 100:
            data['communication_log'] = data['communication_log'][-100:]

    def generate_status_report(self) -> Dict:
        """Generate comprehensive status report."""
        try:
            data = self.load_coordination_data()

            # Calculate metrics
            overall_progress = self.calculate_overall_progress()

            # Get active issues
            active_conflicts = self.get_active_conflicts()
            pending_deps = [
                dep for dep in data.get('dependencies', [])
                if dep.get('status') == 'PENDING'
            ]

            # Squad status summary
            squads = data.get('squads', {})
            squad_summary = {}

            for squad_id, squad_data in squads.items():
                squad_summary[squad_id] = {
                    "status": squad_data.get('status'),
                    "progress": squad_data.get('coverage_percentage', 0),
                    "tests": squad_data.get('tests_created', 0),
                    "last_update": squad_data.get('last_update'),
                    "blockers": len(squad_data.get('blockers', []))
                }

            report = {
                "operation_id": data.get('operation_id'),
                "status": data.get('status'),
                "overall_progress": overall_progress,
                "squad_summary": squad_summary,
                "active_conflicts": len(active_conflicts),
                "pending_dependencies": len(pending_deps),
                "generated_at": datetime.utcnow().isoformat() + 'Z'
            }

            return report

        except Exception as e:
            self.logger.error(f"Error generating status report: {e}")
            return {"error": str(e)}

    def emergency_rebalance(self, reason: str) -> Dict:
        """Trigger emergency squad rebalancing."""
        try:
            self.logger.critical(f"Emergency rebalancing triggered: {reason}")

            data = self.load_coordination_data()

            # Add emergency log
            self._add_communication_log(
                data,
                "coordination-system",
                "EMERGENCY_REBALANCE",
                f"Emergency rebalancing triggered: {reason}",
                "CRITICAL"
            )

            # Update operation status
            data['status'] = 'EMERGENCY_REBALANCING'

            # Save data
            self.save_coordination_data(data)

            return {
                "status": "EMERGENCY_INITIATED",
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "next_action": "Manual intervention required"
            }

        except Exception as e:
            self.logger.error(f"Error during emergency rebalancing: {e}")
            return {"status": "ERROR", "error": str(e)}


# Utility functions for squad coordination
def create_squad_progress(squad_id: str, coverage: float, tests_created: int,
                         tests_passing: int = 0, tests_failing: int = 0,
                         security_tests: int = 0, performance_benchmarks: int = 0,
                         status: SquadStatus = SquadStatus.ACTIVE,
                         blockers: List[str] = None) -> SquadProgress:
    """Create a SquadProgress object with current timestamp."""
    return SquadProgress(
        squad_id=squad_id,
        coverage_percentage=coverage,
        tests_created=tests_created,
        tests_passing=tests_passing,
        tests_failing=tests_failing,
        security_tests=security_tests,
        performance_benchmarks=performance_benchmarks,
        last_update=datetime.utcnow().isoformat() + 'Z',
        status=status,
        blockers=blockers or []
    )


def check_squad_health(coord_utils: CoordinationUtils, squad_id: str) -> Dict:
    """Check health status of a squad."""
    squad_status = coord_utils.get_squad_status(squad_id)

    if not squad_status:
        return {"health": "UNKNOWN", "message": "Squad not found"}

    # Check last update time
    last_update = squad_status.get('last_update')
    if last_update:
        try:
            last_update_time = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            time_since_update = datetime.utcnow().replace(tzinfo=last_update_time.tzinfo) - last_update_time

            if time_since_update > timedelta(minutes=20):
                return {"health": "STALE", "message": "No updates for >20 minutes"}
        except:
            pass

    # Check for blockers
    blockers = squad_status.get('blockers', [])
    if blockers:
        return {"health": "BLOCKED", "message": f"Blocked by: {', '.join(blockers)}"}

    # Check coverage progress
    coverage = squad_status.get('coverage_percentage', 0)
    if coverage < 10:
        return {"health": "SLOW_START", "message": "Low coverage progress"}

    return {"health": "HEALTHY", "message": "Squad operating normally"}


# Example usage and testing functions
if __name__ == "__main__":
    # Initialize coordination utilities
    coord_utils = CoordinationUtils()

    # Example: Register squad progress
    progress = create_squad_progress(
        squad_id="SQUAD_1",
        coverage=75.5,
        tests_created=45,
        tests_passing=42,
        tests_failing=3,
        security_tests=12
    )

    success = coord_utils.register_squad_progress(progress)
    print(f"Progress registration: {'Success' if success else 'Failed'}")

    # Example: Request dependency
    dep_id = coord_utils.request_dependency(
        "SQUAD_2", "SQUAD_1", "auth_fixtures",
        "Need admin authentication fixtures for config tests"
    )
    print(f"Dependency requested: {dep_id}")

    # Generate status report
    report = coord_utils.generate_status_report()
    print("Status Report:", json.dumps(report, indent=2))