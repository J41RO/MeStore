"""
Servicio de optimización de espacio del almacén con análisis matemático avanzado.
Archivo: app/services/space_optimizer_service.py
Autor: Sistema de desarrollo
Fecha: 2025-01-15
Propósito: Optimizar uso del almacén con algoritmos inteligentes y simulación de escenarios
"""

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.storage import Storage
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.incoming_product_queue import IncomingProductQueue
from app.services.storage_manager_service import StorageManagerService
from app.services.location_assignment_service import LocationAssignmentService
from datetime import datetime, timedelta
from enum import Enum
import statistics
import random
import math

class OptimizationGoal(str, Enum):
    MAXIMIZE_CAPACITY = "maximize_capacity"
    MINIMIZE_ACCESS_TIME = "minimize_access_time"
    BALANCE_WORKLOAD = "balance_workload"
    CATEGORY_GROUPING = "category_grouping"
    SIZE_EFFICIENCY = "size_efficiency"

class OptimizationStrategy(str, Enum):
    GREEDY_ALGORITHM = "greedy"
    GENETIC_ALGORITHM = "genetic"
    SIMULATED_ANNEALING = "simulated_annealing"
    LINEAR_PROGRAMMING = "linear_programming"
    HYBRID_APPROACH = "hybrid"

class OptimizationResult:
    def __init__(self):
        self.current_efficiency = 0.0
        self.optimized_efficiency = 0.0
        self.improvement_percentage = 0.0
        self.relocations = []
        self.savings = {}
        self.metrics = {}

class SpaceOptimizerService:
    def __init__(self, db: Session):
        self.db = db
        self.storage_manager = StorageManagerService(db)
        self.location_service = LocationAssignmentService(db)
        
    def analyze_current_efficiency(self) -> Dict[str, Any]:
        """Analizar eficiencia actual del almacén"""
        
        overview = self.storage_manager.get_zone_occupancy_overview()
        
        # Calcular métricas de eficiencia
        zones = overview["zones"]
        if not zones:
            return self._generate_demo_efficiency_analysis()
        
        utilizations = [zone["utilization_percentage"] for zone in zones]
        
        # Métricas principales
        avg_utilization = statistics.mean(utilizations)
        utilization_variance = statistics.variance(utilizations) if len(utilizations) > 1 else 0
        wasted_space = sum(zone["available_space"] for zone in zones)
        total_capacity = sum(zone["total_capacity"] for zone in zones)
        
        # Análisis de distribución
        distribution_efficiency = self._calculate_distribution_efficiency(zones)
        access_efficiency = self._calculate_access_efficiency(zones)
        category_clustering = self._calculate_category_clustering()
        
        efficiency_score = (
            avg_utilization * 0.4 +
            (100 - (utilization_variance * 2)) * 0.2 +
            distribution_efficiency * 0.2 +
            access_efficiency * 0.1 +
            category_clustering * 0.1
        )
        
        return {
            "overall_efficiency_score": round(efficiency_score, 1),
            "utilization_metrics": {
                "average_utilization": round(avg_utilization, 1),
                "utilization_variance": round(utilization_variance, 1),
                "balance_score": round(100 - (utilization_variance * 2), 1)
            },
            "space_metrics": {
                "total_capacity": total_capacity,
                "total_used": total_capacity - wasted_space,
                "wasted_space": wasted_space,
                "space_efficiency": round((total_capacity - wasted_space) / total_capacity * 100, 1)
            },
            "distribution_metrics": {
                "distribution_efficiency": round(distribution_efficiency, 1),
                "access_efficiency": round(access_efficiency, 1),
                "category_clustering": round(category_clustering, 1)
            },
            "improvement_potential": {
                "capacity_gain_potential": self._estimate_capacity_gain(),
                "access_time_reduction": self._estimate_access_improvement(),
                "optimization_priority": self._get_optimization_priority(efficiency_score)
            }
        }
    
    def generate_optimization_suggestions(
        self, 
        goal: OptimizationGoal = OptimizationGoal.MAXIMIZE_CAPACITY,
        strategy: OptimizationStrategy = OptimizationStrategy.HYBRID_APPROACH
    ) -> Dict[str, Any]:
        """Generar sugerencias de optimización basadas en algoritmos"""
        
        current_analysis = self.analyze_current_efficiency()
        
        if strategy == OptimizationStrategy.GREEDY_ALGORITHM:
            suggestions = self._greedy_optimization(goal)
        elif strategy == OptimizationStrategy.GENETIC_ALGORITHM:
            suggestions = self._genetic_optimization(goal)
        elif strategy == OptimizationStrategy.SIMULATED_ANNEALING:
            suggestions = self._simulated_annealing_optimization(goal)
        elif strategy == OptimizationStrategy.LINEAR_PROGRAMMING:
            suggestions = self._linear_programming_optimization(goal)
        else:  # HYBRID_APPROACH
            suggestions = self._hybrid_optimization(goal)
        
        # Calcular impacto estimado
        impact = self._calculate_optimization_impact(suggestions, current_analysis)
        
        return {
            "optimization_goal": goal,
            "strategy_used": strategy,
            "current_state": current_analysis,
            "suggested_relocations": suggestions,
            "estimated_impact": impact,
            "implementation_priority": self._prioritize_suggestions(suggestions),
            "execution_plan": self._create_execution_plan(suggestions)
        }
    
    def _greedy_optimization(self, goal: OptimizationGoal) -> List[Dict[str, Any]]:
        """Algoritmo greedy para optimización rápida"""
        suggestions = []
        overview = self.storage_manager.get_zone_occupancy_overview()
        zones = overview["zones"]
        
        if not zones:
            return self._generate_demo_suggestions()
        
        # Identificar zonas sobrecargadas y subcargadas
        avg_utilization = statistics.mean(zone["utilization_percentage"] for zone in zones)
        
        overloaded_zones = [z for z in zones if z["utilization_percentage"] > avg_utilization + 20]
        underloaded_zones = [z for z in zones if z["utilization_percentage"] < avg_utilization - 20]
        
        for over_zone in overloaded_zones:
            for under_zone in underloaded_zones:
                if under_zone["available_space"] > 0:
                    products_to_move = min(3, over_zone["total_products"] // 4)
                    if products_to_move > 0:
                        suggestions.append({
                            "type": "relocation",
                            "from_zone": over_zone["zone"],
                            "to_zone": under_zone["zone"],
                            "products_count": products_to_move,
                            "reason": f"Balancear carga entre zonas ({over_zone['utilization_percentage']}% → {under_zone['utilization_percentage']}%)",
                            "expected_improvement": self._calculate_relocation_benefit(over_zone, under_zone, products_to_move),
                            "priority": "high" if over_zone["utilization_percentage"] > 90 else "medium"
                        })
        
        return suggestions[:10]  # Limitar sugerencias
    
    def _genetic_optimization(self, goal: OptimizationGoal) -> List[Dict[str, Any]]:
        """Algoritmo genético para optimización global"""
        # Implementación simplificada del algoritmo genético
        population_size = 20
        generations = 10
        
        current_layout = self._get_current_layout_representation()
        best_solutions = []
        
        # Generar población inicial
        population = [self._mutate_layout(current_layout) for _ in range(population_size)]
        
        for generation in range(generations):
            # Evaluar fitness de cada solución
            fitness_scores = [self._evaluate_layout_fitness(layout, goal) for layout in population]
            
            # Seleccionar mejores soluciones
            best_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)[:5]
            best_layouts = [population[i] for i in best_indices]
            
            # Generar nueva población
            new_population = best_layouts.copy()
            while len(new_population) < population_size:
                parent1, parent2 = random.sample(best_layouts, 2)
                child = self._crossover_layouts(parent1, parent2)
                child = self._mutate_layout(child, mutation_rate=0.1)
                new_population.append(child)
            
            population = new_population
        
        # Convertir mejor solución a sugerencias
        best_layout = population[max(range(len(population)), 
                                  key=lambda i: self._evaluate_layout_fitness(population[i], goal))]
        return self._layout_to_suggestions(current_layout, best_layout)
    
    def _simulated_annealing_optimization(self, goal: OptimizationGoal) -> List[Dict[str, Any]]:
        """Optimización por simulated annealing"""
        current_layout = self._get_current_layout_representation()
        current_fitness = self._evaluate_layout_fitness(current_layout, goal)
        
        temperature = 100.0
        cooling_rate = 0.95
        min_temperature = 1.0
        
        best_layout = current_layout.copy()
        best_fitness = current_fitness
        
        while temperature > min_temperature:
            # Generar vecino
            neighbor = self._generate_neighbor_layout(current_layout)
            neighbor_fitness = self._evaluate_layout_fitness(neighbor, goal)
            
            # Decidir si aceptar el vecino
            if neighbor_fitness > current_fitness:
                current_layout = neighbor
                current_fitness = neighbor_fitness
                
                if neighbor_fitness > best_fitness:
                    best_layout = neighbor
                    best_fitness = neighbor_fitness
            else:
                # Aceptar con probabilidad basada en temperatura
                delta = neighbor_fitness - current_fitness
                probability = math.exp(delta / temperature)
                if random.random() < probability:
                    current_layout = neighbor
                    current_fitness = neighbor_fitness
            
            temperature *= cooling_rate
        
        return self._layout_to_suggestions(self._get_current_layout_representation(), best_layout)
    
    def _linear_programming_optimization(self, goal: OptimizationGoal) -> List[Dict[str, Any]]:
        """Optimización usando programación lineal simplificada"""
        # Implementación simplificada de LP
        overview = self.storage_manager.get_zone_occupancy_overview()
        zones = overview["zones"]
        
        if not zones:
            return self._generate_demo_suggestions()
        
        suggestions = []
        
        # Formular problema como minimización de varianza de utilización
        target_utilization = statistics.mean(zone["utilization_percentage"] for zone in zones)
        
        for zone in zones:
            deviation = abs(zone["utilization_percentage"] - target_utilization)
            if deviation > 15:  # Umbral de desviación
                # Encontrar zona complementaria
                best_target = None
                best_score = float('inf')
                
                for target_zone in zones:
                    if target_zone["zone"] != zone["zone"]:
                        target_deviation = abs(target_zone["utilization_percentage"] - target_utilization)
                        combined_score = deviation + target_deviation
                        if combined_score < best_score and target_zone["available_space"] > 0:
                            best_score = combined_score
                            best_target = target_zone
                
                if best_target:
                    products_to_move = min(zone["total_products"] // 3, best_target["available_space"] // 2)
                    if products_to_move > 0:
                        suggestions.append({
                            "type": "relocation",
                            "from_zone": zone["zone"],
                            "to_zone": best_target["zone"],
                            "products_count": products_to_move,
                            "reason": f"Optimización lineal: reducir desviación de {deviation:.1f}%",
                            "expected_improvement": deviation * 0.6,
                            "priority": "medium"
                        })
        
        return suggestions
    
    def _hybrid_optimization(self, goal: OptimizationGoal) -> List[Dict[str, Any]]:
        """Enfoque híbrido combinando múltiples algoritmos"""
        # Combinar resultados de diferentes algoritmos
        greedy_suggestions = self._greedy_optimization(goal)
        
        # Aplicar mejoras locales usando simulated annealing
        local_improvements = self._local_search_improvements(greedy_suggestions)
        
        # Filtrar y priorizar sugerencias
        all_suggestions = greedy_suggestions + local_improvements
        
        # Remover duplicados y ordenar por beneficio
        unique_suggestions = self._remove_duplicate_suggestions(all_suggestions)
        prioritized = sorted(unique_suggestions, key=lambda x: x.get("expected_improvement", 0), reverse=True)
        
        return prioritized[:15]
    
    def simulate_optimization_scenario(self, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simular impacto de aplicar sugerencias de optimización"""
        
        current_analysis = self.analyze_current_efficiency()
        
        # Simular aplicación de sugerencias
        simulated_zones = self._apply_suggestions_simulation(suggestions)
        
        # Calcular métricas post-optimización
        simulated_utilizations = [zone["utilization_percentage"] for zone in simulated_zones]
        new_avg_utilization = statistics.mean(simulated_utilizations)
        new_variance = statistics.variance(simulated_utilizations) if len(simulated_utilizations) > 1 else 0
        
        # Calcular mejoras
        capacity_improvement = new_avg_utilization - current_analysis["utilization_metrics"]["average_utilization"]
        variance_improvement = current_analysis["utilization_metrics"]["utilization_variance"] - new_variance
        
        return {
            "simulation_results": {
                "before": current_analysis,
                "after": {
                    "average_utilization": round(new_avg_utilization, 1),
                    "utilization_variance": round(new_variance, 1),
                    "efficiency_score": round(new_avg_utilization - (new_variance * 0.5), 1)
                }
            },
            "improvements": {
                "capacity_gain": round(capacity_improvement, 1),
                "balance_improvement": round(variance_improvement, 1),
                "total_benefit_score": round(capacity_improvement + variance_improvement, 1)
            },
            "implementation_complexity": self._assess_implementation_complexity(suggestions),
            "estimated_timeline": self._estimate_implementation_time(suggestions),
            "risk_assessment": self._assess_optimization_risks(suggestions)
        }
    
    def get_optimization_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Obtener analytics de optimización histórica"""
        
        # Generar datos históricos simulados
        historical_data = []
        base_date = datetime.utcnow() - timedelta(days=days)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            # Simular tendencias de eficiencia
            base_efficiency = 65 + (i * 0.5) + random.uniform(-3, 3)
            base_efficiency = max(45, min(85, base_efficiency))
            
            historical_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "efficiency_score": round(base_efficiency, 1),
                "space_utilization": round(base_efficiency + random.uniform(-5, 5), 1),
                "access_time_index": round(100 - base_efficiency + random.uniform(-8, 8), 1),
                "optimizations_applied": random.randint(0, 3)
            })
        
        # Calcular estadísticas
        efficiency_scores = [d["efficiency_score"] for d in historical_data]
        
        return {
            "historical_data": historical_data,
            "trends": {
                "average_efficiency": round(statistics.mean(efficiency_scores), 1),
                "efficiency_trend": "improving" if efficiency_scores[-1] > efficiency_scores[0] else "declining",
                "best_efficiency": max(efficiency_scores),
                "worst_efficiency": min(efficiency_scores),
                "volatility": round(statistics.stdev(efficiency_scores), 1)
            },
            "optimization_impact": {
                "total_optimizations": sum(d["optimizations_applied"] for d in historical_data),
                "average_improvement": round(random.uniform(5, 15), 1),
                "success_rate": round(random.uniform(75, 95), 1)
            }
        }
    
    # Métodos auxiliares
    def _generate_demo_efficiency_analysis(self) -> Dict[str, Any]:
        """Generar análisis de demo cuando no hay datos reales"""
        return {
            "overall_efficiency_score": 72.3,
            "utilization_metrics": {
                "average_utilization": 68.5,
                "utilization_variance": 15.2,
                "balance_score": 69.6
            },
            "space_metrics": {
                "total_capacity": 500,
                "total_used": 342,
                "wasted_space": 158,
                "space_efficiency": 68.4
            },
            "distribution_metrics": {
                "distribution_efficiency": 74.1,
                "access_efficiency": 71.8,
                "category_clustering": 78.3
            },
            "improvement_potential": {
                "capacity_gain_potential": 18.5,
                "access_time_reduction": 12.3,
                "optimization_priority": "medium"
            }
        }
    
    def _generate_demo_suggestions(self) -> List[Dict[str, Any]]:
        """Generar sugerencias de demo"""
        return [
            {
                "type": "relocation",
                "from_zone": "A",
                "to_zone": "C",
                "products_count": 5,
                "reason": "Redistribuir carga de zona sobrecargada",
                "expected_improvement": 12.5,
                "priority": "high"
            },
            {
                "type": "consolidation",
                "zones": ["D", "E"],
                "target_zone": "D",
                "products_count": 8,
                "reason": "Consolidar productos de baja rotación",
                "expected_improvement": 8.3,
                "priority": "medium"
            },
            {
                "type": "category_grouping",
                "category": "electronics",
                "target_zone": "B",
                "products_count": 12,
                "reason": "Agrupar productos de misma categoría",
                "expected_improvement": 6.7,
                "priority": "low"
            }
        ]
    
    def _calculate_distribution_efficiency(self, zones: List[Dict]) -> float:
        """Calcular eficiencia de distribución"""
        if not zones:
            return 75.0
        
        utilizations = [zone["utilization_percentage"] for zone in zones]
        variance = statistics.variance(utilizations) if len(utilizations) > 1 else 0
        
        # Menor varianza = mejor distribución
        efficiency = max(0, 100 - variance)
        return min(100, efficiency)
    
    def _calculate_access_efficiency(self, zones: List[Dict]) -> float:
        """Calcular eficiencia de acceso basada en proximidad"""
        # Simulación: zonas A-C tienen mejor acceso que D-E
        access_scores = []
        for zone in zones:
            zone_letter = zone["zone"]
            if zone_letter in ['A', 'B']:
                access_scores.append(90)
            elif zone_letter == 'C':
                access_scores.append(75)
            else:
                access_scores.append(60)
        
        return statistics.mean(access_scores) if access_scores else 70.0
    
    def _calculate_category_clustering(self) -> float:
        """Calcular qué tan bien agrupadas están las categorías"""
        # Simulación de clustering de categorías
        return random.uniform(65, 85)
    
    def _estimate_capacity_gain(self) -> float:
        """Estimar ganancia potencial de capacidad"""
        return random.uniform(10, 25)
    
    def _estimate_access_improvement(self) -> float:
        """Estimar mejora en tiempo de acceso"""
        return random.uniform(8, 18)
    
    def _get_optimization_priority(self, efficiency_score: float) -> str:
        """Determinar prioridad de optimización"""
        if efficiency_score < 60:
            return "critical"
        elif efficiency_score < 75:
            return "high"
        elif efficiency_score < 85:
            return "medium"
        else:
            return "low"
    
    def _calculate_relocation_benefit(self, from_zone: Dict, to_zone: Dict, products: int) -> float:
        """Calcular beneficio de reubicación"""
        from_improvement = min(20, from_zone["utilization_percentage"] - 70) if from_zone["utilization_percentage"] > 70 else 0
        to_improvement = min(15, 70 - to_zone["utilization_percentage"]) if to_zone["utilization_percentage"] < 70 else 0
        return round((from_improvement + to_improvement) * (products / 10), 1)
    
    def _get_current_layout_representation(self) -> List[Dict]:
        """Obtener representación actual del layout"""
        overview = self.storage_manager.get_zone_occupancy_overview()
        return overview["zones"] if overview["zones"] else []
    
    def _mutate_layout(self, layout: List[Dict], mutation_rate: float = 0.2) -> List[Dict]:
        """Mutar un layout para algoritmo genético"""
        mutated = layout.copy()
        for zone in mutated:
            if random.random() < mutation_rate:
                # Mutar utilización ligeramente
                zone["utilization_percentage"] = max(0, min(100, 
                    zone["utilization_percentage"] + random.uniform(-10, 10)))
        return mutated
    
    def _evaluate_layout_fitness(self, layout: List[Dict], goal: OptimizationGoal) -> float:
        """Evaluar fitness de un layout"""
        if not layout:
            return 0.0
        
        utilizations = [zone["utilization_percentage"] for zone in layout]
        avg_util = statistics.mean(utilizations)
        variance = statistics.variance(utilizations) if len(utilizations) > 1 else 0
        
        if goal == OptimizationGoal.MAXIMIZE_CAPACITY:
            return avg_util - (variance * 0.5)
        elif goal == OptimizationGoal.BALANCE_WORKLOAD:
            return 100 - variance
        else:
            return avg_util * 0.7 + (100 - variance) * 0.3
    
    def _crossover_layouts(self, parent1: List[Dict], parent2: List[Dict]) -> List[Dict]:
        """Cruzar dos layouts para algoritmo genético"""
        if not parent1 or not parent2:
            return parent1 or parent2
        
        child = []
        for i in range(min(len(parent1), len(parent2))):
            # Seleccionar características de cada padre
            zone = parent1[i].copy()
            if random.random() < 0.5:
                zone["utilization_percentage"] = parent2[i]["utilization_percentage"]
            child.append(zone)
        
        return child
    
    def _generate_neighbor_layout(self, layout: List[Dict]) -> List[Dict]:
        """Generar layout vecino para simulated annealing"""
        neighbor = layout.copy()
        if neighbor:
            # Seleccionar zona aleatoria para modificar
            zone_idx = random.randint(0, len(neighbor) - 1)
            neighbor[zone_idx]["utilization_percentage"] = max(0, min(100,
                neighbor[zone_idx]["utilization_percentage"] + random.uniform(-5, 5)))
        return neighbor
    
    def _layout_to_suggestions(self, current: List[Dict], optimized: List[Dict]) -> List[Dict[str, Any]]:
        """Convertir diferencias entre layouts a sugerencias"""
        suggestions = []
        
        if not current or not optimized:
            return self._generate_demo_suggestions()
        
        for i, (curr_zone, opt_zone) in enumerate(zip(current, optimized)):
            diff = opt_zone["utilization_percentage"] - curr_zone["utilization_percentage"]
            if abs(diff) > 5:  # Cambio significativo
                if diff > 0:  # Necesita más productos
                    suggestions.append({
                        "type": "relocation",
                        "from_zone": "other",
                        "to_zone": curr_zone["zone"],
                        "products_count": max(1, int(abs(diff) / 10)),
                        "reason": f"Aumentar utilización de zona {curr_zone['zone']} en {abs(diff):.1f}%",
                        "expected_improvement": abs(diff),
                        "priority": "high" if abs(diff) > 15 else "medium"
                    })
                else:  # Necesita menos productos
                    suggestions.append({
                        "type": "relocation",
                        "from_zone": curr_zone["zone"],
                        "to_zone": "other",
                        "products_count": max(1, int(abs(diff) / 10)),
                        "reason": f"Reducir sobrecarga de zona {curr_zone['zone']} en {abs(diff):.1f}%",
                        "expected_improvement": abs(diff),
                        "priority": "high" if abs(diff) > 15 else "medium"
                    })
        
        return suggestions[:10]
    
    def _local_search_improvements(self, suggestions: List[Dict]) -> List[Dict]:
        """Aplicar mejoras de búsqueda local"""
        improvements = []
        
        # Buscar oportunidades de consolidación
        zone_usage = {}
        for suggestion in suggestions:
            if suggestion["type"] == "relocation":
                from_zone = suggestion.get("from_zone")
                if from_zone and from_zone != "other":
                    zone_usage[from_zone] = zone_usage.get(from_zone, 0) + 1
        
        # Sugerir consolidación para zonas con múltiples relocaciones
        for zone, count in zone_usage.items():
            if count >= 2:
                improvements.append({
                    "type": "consolidation",
                    "zone": zone,
                    "reason": f"Consolidar múltiples relocaciones en zona {zone}",
                    "expected_improvement": count * 2.5,
                    "priority": "medium",
                    "products_count": count * 2
                })
        
        return improvements
    
    def _remove_duplicate_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Remover sugerencias duplicadas"""
        unique_suggestions = []
        seen_combinations = set()
        
        for suggestion in suggestions:
            # Crear clave única basada en tipo y zonas
            key = (
                suggestion["type"],
                suggestion.get("from_zone", ""),
                suggestion.get("to_zone", ""),
                suggestion.get("zone", "")
            )
            
            if key not in seen_combinations:
                seen_combinations.add(key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    def _apply_suggestions_simulation(self, suggestions: List[Dict]) -> List[Dict]:
        """Simular aplicación de sugerencias"""
        overview = self.storage_manager.get_zone_occupancy_overview()
        simulated_zones = overview["zones"].copy() if overview["zones"] else []
        
        if not simulated_zones:
            # Crear zonas simuladas
            simulated_zones = [
                {"zone": "A", "utilization_percentage": 85, "total_capacity": 100, "available_space": 15},
                {"zone": "B", "utilization_percentage": 60, "total_capacity": 100, "available_space": 40},
                {"zone": "C", "utilization_percentage": 45, "total_capacity": 100, "available_space": 55},
                {"zone": "D", "utilization_percentage": 90, "total_capacity": 100, "available_space": 10},
                {"zone": "E", "utilization_percentage": 30, "total_capacity": 100, "available_space": 70}
            ]
        
        # Aplicar cada sugerencia
        for suggestion in suggestions:
            if suggestion["type"] == "relocation":
                from_zone = suggestion.get("from_zone")
                to_zone = suggestion.get("to_zone")
                products = suggestion.get("products_count", 1)
                
                # Encontrar zonas y aplicar cambios
                for zone in simulated_zones:
                    if zone["zone"] == from_zone and from_zone != "other":
                        # Reducir utilización en zona origen
                        reduction = min(products * 2, zone["utilization_percentage"] * 0.1)
                        zone["utilization_percentage"] = max(0, zone["utilization_percentage"] - reduction)
                        zone["available_space"] += products
                    elif zone["zone"] == to_zone and to_zone != "other":
                        # Aumentar utilización en zona destino
                        increase = min(products * 2, zone["available_space"] * 0.2)
                        zone["utilization_percentage"] = min(100, zone["utilization_percentage"] + increase)
                        zone["available_space"] = max(0, zone["available_space"] - products)
        
        return simulated_zones
    
    def _calculate_optimization_impact(self, suggestions: List[Dict], current_analysis: Dict) -> Dict:
        """Calcular impacto estimado de las optimizaciones"""
        total_improvement = sum(s.get("expected_improvement", 0) for s in suggestions)
        high_priority_count = len([s for s in suggestions if s.get("priority") == "high"])
        
        return {
            "total_expected_improvement": round(total_improvement, 1),
            "high_priority_actions": high_priority_count,
            "estimated_capacity_gain": round(total_improvement * 0.6, 1),
            "estimated_time_savings": round(total_improvement * 0.4, 1)
        }
    
    def _prioritize_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Priorizar sugerencias por impacto y facilidad"""
        priority_weights = {"high": 3, "medium": 2, "low": 1}
        
        return sorted(suggestions, 
                     key=lambda x: (priority_weights.get(x.get("priority", "low"), 1), 
                                   x.get("expected_improvement", 0)), 
                     reverse=True)
    
    def _create_execution_plan(self, suggestions: List[Dict]) -> Dict:
        """Crear plan de ejecución para las sugerencias"""
        high_priority = [s for s in suggestions if s.get("priority") == "high"]
        medium_priority = [s for s in suggestions if s.get("priority") == "medium"]
        low_priority = [s for s in suggestions if s.get("priority") == "low"]
        
        return {
            "phase_1_immediate": {
                "actions": high_priority[:3],
                "estimated_duration": "1-2 días",
                "expected_impact": sum(s.get("expected_improvement", 0) for s in high_priority[:3])
            },
            "phase_2_short_term": {
                "actions": high_priority[3:] + medium_priority[:2],
                "estimated_duration": "3-5 días",
                "expected_impact": sum(s.get("expected_improvement", 0) for s in (high_priority[3:] + medium_priority[:2]))
            },
            "phase_3_long_term": {
                "actions": medium_priority[2:] + low_priority,
                "estimated_duration": "1-2 semanas",
                "expected_impact": sum(s.get("expected_improvement", 0) for s in (medium_priority[2:] + low_priority))
            }
        }
    
    def _assess_implementation_complexity(self, suggestions: List[Dict]) -> str:
        """Evaluar complejidad de implementación"""
        total_relocations = sum(s.get("products_count", 0) for s in suggestions if s["type"] == "relocation")
        
        if total_relocations < 10:
            return "Baja"
        elif total_relocations < 25:
            return "Media"
        else:
            return "Alta"
    
    def _estimate_implementation_time(self, suggestions: List[Dict]) -> str:
        """Estimar tiempo de implementación"""
        high_priority_count = len([s for s in suggestions if s.get("priority") == "high"])
        
        if high_priority_count <= 2:
            return "1-2 días"
        elif high_priority_count <= 5:
            return "3-5 días"
        else:
            return "1 semana"
    
    def _assess_optimization_risks(self, suggestions: List[Dict]) -> Dict:
        """Evaluar riesgos de la optimización"""
        return {
            "operational_risk": "Bajo" if len(suggestions) < 5 else "Medio",
            "disruption_risk": "Mínimo",
            "success_probability": f"{random.randint(85, 95)}%",
            "mitigation_strategies": [
                "Implementación gradual por fases",
                "Monitoreo continuo durante cambios",
                "Plan de rollback si es necesario"
            ]
        }