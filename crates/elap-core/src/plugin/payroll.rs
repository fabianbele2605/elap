//! PayrollPlugin - Análisis y cálculos de nómina
//!
//! Plugin especializado para:
//! - Análisis de salarios y datos de nómina
//! - Cálculos de impuestos y beneficios
//! - Consultas sobre estructura salarial
//! - Integración con RAG de datos de nómina

use serde::{Deserialize, Serialize};
use crate::error::{ElapError, ResultadoElap};

/// Resultado de análisis salarial
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SalaryAnalysis {
    pub department: String,
    pub employee_count: usize,
    pub average_salary: f64,
    pub min_salary: f64,
    pub max_salary: f64,
    pub total_payroll: f64,
}

/// Cálculo de beneficios
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BenefitCalculation {
    pub gross_salary: f64,
    pub health_contribution: f64,     // 4% empleado
    pub pension_contribution: f64,    // 4% empleado
    pub transport_allowance: f64,
    pub total_deductions: f64,
    pub net_salary: f64,
    pub employer_health: f64,         // 8.5% empleador
    pub employer_pension: f64,        // 12% empleador
    pub severance_monthly: f64,       // 8.33%
    pub bonus_monthly: f64,           // 8.33%
    pub vacation_monthly: f64,        // 4.17%
    pub total_employer_cost: f64,
}

/// Datos agregados de nómina
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PayrollSummary {
    pub total_employees: usize,
    pub total_gross_payroll: f64,
    pub total_net_payroll: f64,
    pub total_employer_contributions: f64,
    pub total_deductions: f64,
    pub average_salary_company: f64,
}

/// Herramienta para calcular salario neto
#[derive(Debug, Clone)]
pub struct SalaryCalculator;

impl SalaryCalculator {
    /// Calcular beneficios y deducciones para un salario bruto
    pub fn calculate_benefits(gross_salary: f64, transport_allowance: f64) -> BenefitCalculation {
        // Cálculos según normativa laboral colombiana
        let health_contribution = gross_salary * 0.04;
        let pension_contribution = gross_salary * 0.04;
        let total_deductions = health_contribution + pension_contribution;
        let net_salary = gross_salary + transport_allowance - total_deductions;

        // Contribuciones del empleador
        let employer_health = gross_salary * 0.085;
        let employer_pension = gross_salary * 0.12;
        let severance_monthly = gross_salary * 0.0833;  // 8.33%
        let bonus_monthly = gross_salary * 0.0833;      // 8.33%
        let vacation_monthly = gross_salary * 0.0417;   // 4.17%

        let total_employer_cost = gross_salary
            + transport_allowance
            + employer_health
            + employer_pension
            + severance_monthly
            + bonus_monthly
            + vacation_monthly;

        BenefitCalculation {
            gross_salary,
            health_contribution,
            pension_contribution,
            transport_allowance,
            total_deductions,
            net_salary,
            employer_health,
            employer_pension,
            severance_monthly,
            bonus_monthly,
            vacation_monthly,
            total_employer_cost,
        }
    }

    /// Validar si salario es válido
    pub fn validate_salary(salary: f64) -> ResultadoElap<()> {
        const MIN_WAGE: f64 = 248.258; // SMLMV 2026 aproximado en miles

        if salary < MIN_WAGE {
            return Err(ElapError::ValidationError(
                format!(
                    "Salario {} por debajo del mínimo {}",
                    salary, MIN_WAGE
                ),
            ));
        }

        Ok(())
    }
}

/// Configuration del PayrollPlugin
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PayrollPluginConfig {
    pub enabled: bool,
    pub timeout_ms: u64,
    pub max_employees_per_query: usize,
    pub cache_results: bool,
}

impl Default for PayrollPluginConfig {
    fn default() -> Self {
        Self {
            enabled: true,
            timeout_ms: 30000,
            max_employees_per_query: 1000,
            cache_results: true,
        }
    }
}

/// Plugin de nómina y análisis salarial
pub struct PayrollPlugin {
    pub config: PayrollPluginConfig,
    pub salary_calculator: SalaryCalculator,
}

impl PayrollPlugin {
    /// Crear nuevo PayrollPlugin
    pub fn new(config: PayrollPluginConfig) -> Self {
        Self {
            config,
            salary_calculator: SalaryCalculator,
        }
    }

    /// Crear con config por defecto
    pub fn default_new() -> Self {
        Self::new(PayrollPluginConfig::default())
    }

    /// Analizar salarios por departamento
    pub fn analyze_department_salaries(
        &self,
        department: &str,
        employees: Vec<f64>,
    ) -> ResultadoElap<SalaryAnalysis> {
        if employees.is_empty() {
            return Err(ElapError::ValidationError(
                "No hay empleados para analizar".to_string(),
            ));
        }

        if employees.len() > self.config.max_employees_per_query {
            return Err(ElapError::ValidationError(
                format!(
                    "Demasiados empleados: {} (máximo: {})",
                    employees.len(),
                    self.config.max_employees_per_query
                ),
            ));
        }

        // Validar cada salario
        for salary in &employees {
            SalaryCalculator::validate_salary(*salary)?;
        }

        // Calcular estadísticas
        let total: f64 = employees.iter().sum();
        let average = total / employees.len() as f64;
        let min = employees
            .iter()
            .cloned()
            .fold(f64::INFINITY, f64::min);
        let max = employees
            .iter()
            .cloned()
            .fold(f64::NEG_INFINITY, f64::max);

        Ok(SalaryAnalysis {
            department: department.to_string(),
            employee_count: employees.len(),
            average_salary: average,
            min_salary: min,
            max_salary: max,
            total_payroll: total,
        })
    }

    /// Generar resumen de nómina agregada
    pub fn generate_payroll_summary(
        &self,
        all_employees: Vec<(String, f64)>, // (departamento, salario)
    ) -> ResultadoElap<PayrollSummary> {
        if all_employees.is_empty() {
            return Err(ElapError::ValidationError(
                "No hay empleados en la nómina".to_string(),
            ));
        }

        let mut total_gross = 0.0;
        let mut total_net = 0.0;
        let mut total_employer = 0.0;

        for (_dept, salary) in &all_employees {
            SalaryCalculator::validate_salary(*salary)?;

            // Asumir allowance estándar
            let calc = SalaryCalculator::calculate_benefits(*salary, 117_346.0);
            total_gross += calc.gross_salary;
            total_net += calc.net_salary;
            total_employer += calc.total_employer_cost;
        }

        let total_deductions = total_gross - total_net;
        let average_salary = total_gross / all_employees.len() as f64;

        Ok(PayrollSummary {
            total_employees: all_employees.len(),
            total_gross_payroll: total_gross,
            total_net_payroll: total_net,
            total_employer_contributions: total_employer - total_gross,
            total_deductions,
            average_salary_company: average_salary,
        })
    }

    /// Calcular impacto de aumento salarial
    pub fn calculate_salary_increase_impact(
        &self,
        current_salary: f64,
        increase_percentage: f64,
    ) -> ResultadoElap<(BenefitCalculation, BenefitCalculation)> {
        SalaryCalculator::validate_salary(current_salary)?;

        let new_salary = current_salary * (1.0 + increase_percentage);

        if new_salary < current_salary {
            return Err(ElapError::ValidationError(
                "El aumento debe ser positivo".to_string(),
            ));
        }

        let current_calc = SalaryCalculator::calculate_benefits(current_salary, 117_346.0);
        let new_calc = SalaryCalculator::calculate_benefits(new_salary, 117_346.0);

        Ok((current_calc, new_calc))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_salary_calculator_basic() {
        let calc = SalaryCalculator::calculate_benefits(3_000_000.0, 117_346.0);
        assert_eq!(calc.gross_salary, 3_000_000.0);
        assert_eq!(calc.health_contribution, 120_000.0);
        assert_eq!(calc.pension_contribution, 120_000.0);
        assert!(calc.net_salary > 0.0);
    }

    #[test]
    fn test_salary_validation() {
        assert!(SalaryCalculator::validate_salary(300_000.0).is_ok());
        assert!(SalaryCalculator::validate_salary(0.0).is_err());
    }

    #[test]
    fn test_payroll_plugin_new() {
        let plugin = PayrollPlugin::default_new();
        assert!(plugin.config.enabled);
        assert_eq!(plugin.config.timeout_ms, 30000);
    }

    #[test]
    fn test_analyze_department_salaries() {
        let plugin = PayrollPlugin::default_new();
        let salaries = vec![2_000_000.0, 3_000_000.0, 4_000_000.0];

        let analysis = plugin
            .analyze_department_salaries("Ventas", salaries)
            .unwrap();

        assert_eq!(analysis.department, "Ventas");
        assert_eq!(analysis.employee_count, 3);
        assert_eq!(analysis.average_salary, 3_000_000.0);
        assert_eq!(analysis.min_salary, 2_000_000.0);
        assert_eq!(analysis.max_salary, 4_000_000.0);
    }

    #[test]
    fn test_analyze_empty_department() {
        let plugin = PayrollPlugin::default_new();
        let result = plugin.analyze_department_salaries("Ventas", vec![]);
        assert!(result.is_err());
    }

    #[test]
    fn test_payroll_summary() {
        let plugin = PayrollPlugin::default_new();
        let employees = vec![
            ("Ventas".to_string(), 3_000_000.0),
            ("Operaciones".to_string(), 2_500_000.0),
        ];

        let summary = plugin.generate_payroll_summary(employees).unwrap();
        assert_eq!(summary.total_employees, 2);
        assert!(summary.total_gross_payroll > 0.0);
    }

    #[test]
    fn test_salary_increase_impact() {
        let plugin = PayrollPlugin::default_new();
        let (current, new) = plugin
            .calculate_salary_increase_impact(3_000_000.0, 0.1)
            .unwrap();

        assert_eq!(current.gross_salary, 3_000_000.0);
        assert!((new.gross_salary - 3_300_000.0).abs() < 1.0);
        assert!(new.net_salary > current.net_salary);
    }

    #[test]
    fn test_benefit_calculations_correctness() {
        let calc = SalaryCalculator::calculate_benefits(1_000_000.0, 117_346.0);

        // Validar porcentajes
        assert_eq!(calc.health_contribution, 40_000.0);      // 4%
        assert_eq!(calc.pension_contribution, 40_000.0);     // 4%
        assert_eq!(calc.employer_health, 85_000.0);          // 8.5%
        assert_eq!(calc.employer_pension, 120_000.0);        // 12%

        // Validar suma
        let expected_net = 1_000_000.0 + 117_346.0 - 80_000.0;
        assert!((calc.net_salary - expected_net).abs() < 1.0);
    }
}
