/**
 * Dashboard de optimización de espacio del almacén con simulador inteligente
 * Archivo: frontend/src/components/admin/SpaceOptimizerDashboard.tsx
 * Autor: Sistema de desarrollo
 * Fecha: 2025-01-15
 * Propósito: Dashboard visual completo para SpaceOptimizer con algoritmos de optimización
 */

import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, RadialBarChart, RadialBar, PieChart, Pie, Cell
} from 'recharts';
import { 
  Zap, Target, TrendingUp, Settings, Play, Eye, CheckCircle, 
  AlertTriangle, Lightbulb, RotateCcw, Brain, Gauge, Activity,
  Filter, Download, Calculator, BarChart3
} from 'lucide-react';

interface OptimizationSuggestion {
  type: string;
  from_zone?: string;
  to_zone?: string;
  products_count: number;
  reason: string;
  expected_improvement: number;
  priority: string;
}

interface EfficiencyAnalysis {
  overall_efficiency_score: number;
  utilization_metrics: {
    average_utilization: number;
    utilization_variance: number;
    balance_score: number;
  };
  space_metrics: {
    total_capacity: number;
    total_used: number;
    wasted_space: number;
    space_efficiency: number;
  };
  distribution_metrics: {
    distribution_efficiency: number;
    access_efficiency: number;
    category_clustering: number;
  };
  improvement_potential: {
    capacity_gain_potential: number;
    access_time_reduction: number;
    optimization_priority: string;
  };
}

interface SimulationResult {
  simulation_results: {
    before: EfficiencyAnalysis;
    after: {
      average_utilization: number;
      utilization_variance: number;
      efficiency_score: number;
    };
  };
  improvements: {
    capacity_gain: number;
    balance_improvement: number;
    total_benefit_score: number;
  };
  implementation_complexity: string;
  estimated_timeline: string;
  risk_assessment: {
    operational_risk: string;
    disruption_risk: string;
    success_probability: string;
  };
}

const SpaceOptimizerDashboard: React.FC = () => {
  const [analysis, setAnalysis] = useState<EfficiencyAnalysis | null>(null);
  const [suggestions, setSuggestions] = useState<OptimizationSuggestion[]>([]);
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [optimizationGoal, setOptimizationGoal] = useState('maximize_capacity');
  const [optimizationStrategy, setOptimizationStrategy] = useState('hybrid');
  const [selectedSuggestions, setSelectedSuggestions] = useState<Set<number>>(new Set());
  const [activeTab, setActiveTab] = useState('overview');
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);

  useEffect(() => {
    loadOptimizerData();
  }, []);

  const loadOptimizerData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      
      if (!token) {
        console.error('❌ No se encontró token de acceso');
        setLoading(false);
        return;
      }
      
      // Cargar análisis de eficiencia
      const analysisResponse = await fetch(
        '/api/v1/admin/space-optimizer/analysis',
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      if (analysisResponse.ok) {
        const analysisData = await analysisResponse.json();
        setAnalysis(analysisData);
      }

      // Cargar analytics
      const analyticsResponse = await fetch(
        '/api/v1/admin/space-optimizer/analytics?days=30',
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setAnalytics(analyticsData);
      }

      // Generar sugerencias iniciales
      await generateSuggestions();

    } catch (error) {
      console.error('Error loading optimizer data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateSuggestions = async () => {
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      const response = await fetch(
        `/api/v1/admin/space-optimizer/suggestions?goal=${optimizationGoal}&strategy=${optimizationStrategy}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggested_relocations || []);
      }
    } catch (error) {
      console.error('Error generating suggestions:', error);
    }
  };

  const simulateOptimization = async () => {
    if (selectedSuggestions.size === 0) {
      alert('Selecciona al menos una sugerencia para simular');
      return;
    }

    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      const selectedSuggestionsList = Array.from(selectedSuggestions).map(index => suggestions[index]);
      
      const response = await fetch(
        '/api/v1/admin/space-optimizer/simulate',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(selectedSuggestionsList)
        }
      );

      if (response.ok) {
        const simulationData = await response.json();
        setSimulation(simulationData);
      }
    } catch (error) {
      console.error('Error simulating optimization:', error);
    }
  };

  const getEfficiencyColor = (score: number) => {
    if (score >= 85) return '#22c55e';
    if (score >= 70) return '#3b82f6';
    if (score >= 55) return '#f59e0b';
    return '#ef4444';
  };

  const getPriorityColor = (priority: string) => {
    const colors: { [key: string]: string } = {
      high: '#ef4444',
      medium: '#f59e0b',
      low: '#22c55e'
    };
    return colors[priority] || '#6b7280';
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <AlertTriangle className="w-4 h-4" />;
      case 'medium': return <Target className="w-4 h-4" />;
      case 'low': return <CheckCircle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const exportAnalysisReport = () => {
    if (!analysis) return;
    
    const report = {
      timestamp: new Date().toISOString(),
      efficiency_analysis: analysis,
      optimization_suggestions: suggestions,
      simulation_results: simulation
    };
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `space-optimization-report-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Brain className="w-12 h-12 mx-auto text-purple-400 mb-4 animate-pulse" />
          <p className="text-gray-600">Analizando eficiencia del almacén...</p>
          <div className="mt-4 w-48 bg-gray-200 rounded-full h-2 mx-auto">
            <div className="bg-purple-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold flex items-center">
            <Brain className="w-6 h-6 mr-2 text-purple-600" />
            Space Optimizer
          </h2>
          <p className="text-gray-600 mt-1">Sistema inteligente de optimización del almacén</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={exportAnalysisReport}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Exportar Reporte
          </button>
          <button
            onClick={loadOptimizerData}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 flex items-center"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Actualizar
          </button>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'overview', name: 'Resumen General', icon: BarChart3 },
            { id: 'optimization', name: 'Optimización', icon: Zap },
            { id: 'simulation', name: 'Simulador', icon: Calculator },
            { id: 'analytics', name: 'Analytics', icon: TrendingUp }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && analysis && (
        <div className="space-y-6">
          {/* Métricas de Eficiencia */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-6 rounded-lg shadow border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Eficiencia General</p>
                  <p className="text-2xl font-bold" style={{ color: getEfficiencyColor(analysis.overall_efficiency_score) }}>
                    {analysis.overall_efficiency_score}%
                  </p>
                </div>
                <Gauge className="w-8 h-8 text-purple-600" />
              </div>
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="h-2 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${analysis.overall_efficiency_score}%`,
                      backgroundColor: getEfficiencyColor(analysis.overall_efficiency_score)
                    }}
                  />
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Potencial de Mejora</p>
                  <p className="text-2xl font-bold text-green-600">
                    +{analysis.improvement_potential.capacity_gain_potential}%
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Capacidad adicional estimada
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Espacio Desperdiciado</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {analysis.space_metrics.wasted_space}
                  </p>
                </div>
                <AlertTriangle className="w-8 h-8 text-orange-600" />
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Unidades sin utilizar
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Prioridad</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {analysis.improvement_potential.optimization_priority.toUpperCase()}
                  </p>
                </div>
                <Target className="w-8 h-8 text-blue-600" />
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Nivel de optimización requerido
              </p>
            </div>
          </div>

          {/* Gráficos de distribución */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold mb-4">Distribución de Métricas</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RadialBarChart cx="50%" cy="50%" innerRadius="10%" outerRadius="80%" data={[
                  { name: 'Distribución', value: analysis.distribution_metrics.distribution_efficiency, fill: '#8b5cf6' },
                  { name: 'Acceso', value: analysis.distribution_metrics.access_efficiency, fill: '#3b82f6' },
                  { name: 'Clustering', value: analysis.distribution_metrics.category_clustering, fill: '#10b981' }
                ]}>
                  <RadialBar dataKey="value" cornerRadius={10} fill="#8884d8" />
                  <Tooltip />
                </RadialBarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border">
              <h3 className="text-lg font-semibold mb-4">Balance de Utilización</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Utilizado', value: analysis.space_metrics.total_used, fill: '#3b82f6' },
                      { name: 'Disponible', value: analysis.space_metrics.wasted_space, fill: '#e5e7eb' }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    <Cell fill="#3b82f6" />
                    <Cell fill="#e5e7eb" />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'optimization' && (
        <div className="space-y-6">
          {/* Configuración de Optimización */}
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold flex items-center">
                <Settings className="w-5 h-5 mr-2 text-gray-600" />
                Configuración de Optimización
              </h3>
              <button
                onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                className="text-purple-600 hover:text-purple-700 text-sm flex items-center"
              >
                <Filter className="w-4 h-4 mr-1" />
                {showAdvancedOptions ? 'Ocultar' : 'Mostrar'} Opciones Avanzadas
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Objetivo Principal</label>
                <select
                  value={optimizationGoal}
                  onChange={(e) => setOptimizationGoal(e.target.value)}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                >
                  <option value="maximize_capacity">Maximizar Capacidad</option>
                  <option value="minimize_access_time">Minimizar Tiempo de Acceso</option>
                  <option value="balance_workload">Balancear Carga de Trabajo</option>
                  <option value="category_grouping">Agrupar por Categorías</option>
                  <option value="size_efficiency">Optimizar por Tamaño</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Estrategia de Algoritmo</label>
                <select
                  value={optimizationStrategy}
                  onChange={(e) => setOptimizationStrategy(e.target.value)}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                >
                  <option value="hybrid">Híbrido (Recomendado)</option>
                  <option value="greedy">Greedy (Rápido)</option>
                  <option value="genetic">Genético (Óptimo)</option>
                  <option value="simulated_annealing">Simulated Annealing</option>
                  <option value="linear_programming">Programación Lineal</option>
                </select>
              </div>

              <div className="flex items-end">
                <button
                  onClick={generateSuggestions}
                  className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 flex items-center justify-center"
                >
                  <Lightbulb className="w-4 h-4 mr-2" />
                  Generar Sugerencias
                </button>
              </div>
            </div>

            {showAdvancedOptions && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Peso de Capacidad (%)</label>
                    <input type="range" min="0" max="100" defaultValue="70" className="w-full" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Peso de Accesibilidad (%)</label>
                    <input type="range" min="0" max="100" defaultValue="30" className="w-full" />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Sugerencias de Optimización */}
          {suggestions.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow border">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold flex items-center">
                  <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
                  Sugerencias de Optimización ({suggestions.length})
                </h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setSelectedSuggestions(new Set(suggestions.map((_, i) => i)))}
                    className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                  >
                    Seleccionar Todas
                  </button>
                  <button
                    onClick={() => setSelectedSuggestions(new Set())}
                    className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                  >
                    Limpiar
                  </button>
                  <button
                    onClick={simulateOptimization}
                    disabled={selectedSuggestions.size === 0}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Simular ({selectedSuggestions.size})
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                {suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      selectedSuggestions.has(index) 
                        ? 'border-purple-300 bg-purple-50 shadow-md' 
                        : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                    }`}
                    onClick={() => {
                      const newSelected = new Set(selectedSuggestions);
                      if (newSelected.has(index)) {
                        newSelected.delete(index);
                      } else {
                        newSelected.add(index);
                      }
                      setSelectedSuggestions(newSelected);
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            checked={selectedSuggestions.has(index)}
                            onChange={() => {}}
                            className="rounded"
                          />
                          <div className="flex items-center space-x-2">
                            {getPriorityIcon(suggestion.priority)}
                            <div>
                              <p className="font-medium">{suggestion.reason}</p>
                              <p className="text-sm text-gray-600">
                                {suggestion.type === 'relocation' && 
                                  `Mover ${suggestion.products_count} productos de Zona ${suggestion.from_zone} → Zona ${suggestion.to_zone}`
                                }
                                {suggestion.type === 'consolidation' && 
                                  `Consolidar ${suggestion.products_count} productos`
                                }
                                {suggestion.type === 'category_grouping' && 
                                  `Reagrupar ${suggestion.products_count} productos por categoría`
                                }
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <p className="text-sm text-gray-600">Mejora Esperada</p>
                          <p className="font-semibold text-green-600">+{suggestion.expected_improvement}%</p>
                        </div>
                        <span 
                          className="px-2 py-1 rounded text-xs font-medium text-white"
                          style={{ backgroundColor: getPriorityColor(suggestion.priority) }}
                        >
                          {suggestion.priority.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'simulation' && simulation && (
        <div className="space-y-6">
          {/* Resultados de Simulación */}
          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Eye className="w-5 h-5 mr-2 text-blue-600" />
              Resultados de Simulación
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="text-center p-4 bg-gray-50 rounded">
                <p className="text-sm text-gray-600 mb-2">Eficiencia Actual</p>
                <p className="text-3xl font-bold text-gray-700">
                  {simulation.simulation_results.before.overall_efficiency_score}%
                </p>
              </div>
              
              <div className="text-center p-4 bg-green-50 rounded">
                <p className="text-sm text-gray-600 mb-2">Eficiencia Proyectada</p>
                <p className="text-3xl font-bold text-green-600">
                  {simulation.simulation_results.after.efficiency_score}%
                </p>
              </div>
              
              <div className="text-center p-4 bg-purple-50 rounded">
                <p className="text-sm text-gray-600 mb-2">Mejora Total</p>
                <p className="text-3xl font-bold text-purple-600">
                  +{simulation.improvements.total_benefit_score}%
                </p>
              </div>
            </div>

            {/* Gráfico de comparación */}
            <div className="mb-6">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={[
                  {
                    name: 'Antes',
                    eficiencia: simulation.simulation_results.before.overall_efficiency_score,
                    utilizacion: simulation.simulation_results.before.utilization_metrics.average_utilization
                  },
                  {
                    name: 'Después',
                    eficiencia: simulation.simulation_results.after.efficiency_score,
                    utilizacion: simulation.simulation_results.after.average_utilization
                  }
                ]}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="eficiencia" fill="#8b5cf6" name="Eficiencia %" />
                  <Bar dataKey="utilizacion" fill="#3b82f6" name="Utilización %" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-4 bg-green-50 border border-green-200 rounded">
                <h4 className="font-medium text-green-800 mb-2">Beneficios Proyectados:</h4>
                <ul className="text-sm text-green-700 space-y-1">
                  <li>• Ganancia de capacidad: +{simulation.improvements.capacity_gain}%</li>
                  <li>• Mejora en balance: +{simulation.improvements.balance_improvement}%</li>
                  <li>• Complejidad: {simulation.implementation_complexity}</li>
                  <li>• Tiempo estimado: {simulation.estimated_timeline}</li>
                </ul>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded">
                <h4 className="font-medium text-blue-800 mb-2">Evaluación de Riesgos:</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Riesgo operacional: {simulation.risk_assessment.operational_risk}</li>
                  <li>• Riesgo de interrupción: {simulation.risk_assessment.disruption_risk}</li>
                  <li>• Probabilidad de éxito: {simulation.risk_assessment.success_probability}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'analytics' && analytics && (
        <div className="space-y-6">
          {/* Tendencias Históricas */}
          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-lg font-semibold mb-4">Tendencias de Eficiencia (30 días)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics.historical_data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="efficiency_score" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  name="Puntuación de Eficiencia"
                />
                <Line 
                  type="monotone" 
                  dataKey="space_utilization" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  name="Utilización de Espacio"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Estadísticas de Optimización */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow border">
              <h4 className="font-semibold mb-3">Resumen de Tendencias</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Eficiencia Promedio:</span>
                  <span className="font-semibold">{analytics.trends.average_efficiency}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Mejor Eficiencia:</span>
                  <span className="font-semibold text-green-600">{analytics.trends.best_efficiency}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Volatilidad:</span>
                  <span className="font-semibold">{analytics.trends.volatility}</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border">
              <h4 className="font-semibold mb-3">Impacto de Optimizaciones</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Optimizaciones:</span>
                  <span className="font-semibold">{analytics.optimization_impact.total_optimizations}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Mejora Promedio:</span>
                  <span className="font-semibold text-green-600">+{analytics.optimization_impact.average_improvement}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tasa de Éxito:</span>
                  <span className="font-semibold">{analytics.optimization_impact.success_rate}%</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow border">
              <h4 className="font-semibold mb-3">Predicciones</h4>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 mb-2">
                  {analytics.trends.efficiency_trend === 'improving' ? '📈' : '📉'}
                </div>
                <p className="text-sm text-gray-600">
                  Tendencia: {analytics.trends.efficiency_trend === 'improving' ? 'Mejorando' : 'Declinando'}
                </p>
                <div className="mt-3 p-2 bg-purple-50 rounded">
                  <p className="text-xs text-purple-700">
                    Proyección: Continuar optimizaciones para mantener tendencia positiva
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SpaceOptimizerDashboard;