//! BenefitsPlugin - Gestión de beneficios y seguridad social
//!
//! Plugin especializado para:
//! - Gestión de EPS, pensión, ARL
//! - Cálculos de cesantías y prima
//! - Información de proveedores
//! - Asesoría sobre beneficios

use serde::{Deserialize, Serialize};
use crate::error::{ElapError, ResultadoElap};

/// Proveedor de seguridad social
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BenefitsProvider {
    pub name: String,
    pub provider_type: ProviderType,
    pub contact: String,
    pub coverage_percentage: f32,
}

/// Tipos de proveedores
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ProviderType {
    EPS,           // Entidad Promotora de Salud
    Pension,       // Fondo de Pensión
    ARL,           // Aseguradora de Riesgos Laborales
    Compensation,  // Caja de Compensación
}

/// Plan de beneficios
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BenefitsPlan {
    pub plan_name: String,
    pub eps: BenefitsProvider,
    pub pension: BenefitsProvider,
    pub arl: BenefitsProvider,
    pub compensation: BenefitsProvider,
    pub annual_cost: f64,
}

/// Cálculo de prestaciones sociales
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SocialBenefits {
    pub severance: f64,           // Cesantías acumuladas
    pub annual_bonus: f64,        // Prima anual
    pub vacation_days: u32,
    pub vacation_cost: f64,
    pub total_accrued: f64,
}

/// Asesoría de beneficios
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BenefitsAdvice {
    pub question: String,
    pub response: String,
    pub related_topics: Vec<String>,
}

/// BenefitsPlugin
pub struct BenefitsPlugin {
    pub enabled: bool,
    pub providers: Vec<BenefitsProvider>,
}

impl BenefitsPlugin {
    /// Crear nuevo BenefitsPlugin
    pub fn new() -> Self {
        Self {
            enabled: true,
            providers: vec![
                BenefitsProvider {
                    name: "Coomeva".to_string(),
                    provider_type: ProviderType::EPS,
                    contact: "eps@coomeva.com.co".to_string(),
                    coverage_percentage: 100.0,
                },
                BenefitsProvider {
                    name: "Protección".to_string(),
                    provider_type: ProviderType::Pension,
                    contact: "info@proteccion.com.co".to_string(),
                    coverage_percentage: 100.0,
                },
                BenefitsProvider {
                    name: "Seguros Monterrey".to_string(),
                    provider_type: ProviderType::ARL,
                    contact: "arl@monterrey.com.co".to_string(),
                    coverage_percentage: 100.0,
                },
            ],
        }
    }

    /// Calcular cesantías acumuladas
    pub fn calculate_severance(
        &self,
        monthly_salary: f64,
        months_worked: u32,
    ) -> ResultadoElap<f64> {
        if monthly_salary <= 0.0 {
            return Err(ElapError::ValidationError("Salario debe ser positivo".to_string()));
        }

        if months_worked == 0 {
            return Ok(0.0);
        }

        // Cesantías: 30 días por año de servicio
        let years = months_worked as f64 / 12.0;
        let severance = (monthly_salary / 30.0) * 30.0 * years;

        Ok(severance)
    }

    /// Calcular prima anual (bono)
    pub fn calculate_annual_bonus(
        &self,
        monthly_salary: f64,
        months_worked: u32,
    ) -> ResultadoElap<f64> {
        if monthly_salary <= 0.0 {
            return Err(ElapError::ValidationError("Salario debe ser positivo".to_string()));
        }

        if months_worked == 0 {
            return Ok(0.0);
        }

        // Prima: 30 días por año de servicio
        let years = months_worked as f64 / 12.0;
        let bonus = (monthly_salary / 30.0) * 30.0 * years;

        Ok(bonus)
    }

    /// Calcular días de vacaciones
    pub fn calculate_vacation_days(&self, months_worked: u32) -> u32 {
        // Colombia: 15 días por año de servicio
        let years = months_worked as u32 / 12;
        let remaining_months = months_worked % 12;

        let full_year_days = years * 15;
        let partial_month_days = if remaining_months > 0 {
            (remaining_months as f32 * 15.0 / 12.0) as u32
        } else {
            0
        };

        full_year_days + partial_month_days
    }

    /// Calcular beneficios sociales totales
    pub fn calculate_total_benefits(
        &self,
        monthly_salary: f64,
        months_worked: u32,
    ) -> ResultadoElap<SocialBenefits> {
        let severance = self.calculate_severance(monthly_salary, months_worked)?;
        let bonus = self.calculate_annual_bonus(monthly_salary, months_worked)?;
        let vacation_days = self.calculate_vacation_days(months_worked);
        let vacation_cost = (monthly_salary / 30.0) * vacation_days as f64;

        Ok(SocialBenefits {
            severance,
            annual_bonus: bonus,
            vacation_days,
            vacation_cost,
            total_accrued: severance + bonus + vacation_cost,
        })
    }

    /// Obtener información de proveedores
    pub fn get_providers_by_type(
        &self,
        provider_type: &ProviderType,
    ) -> Vec<BenefitsProvider> {
        self.providers
            .iter()
            .filter(|p| &p.provider_type == provider_type)
            .cloned()
            .collect()
    }

    /// Crear plan de beneficios sugerido
    pub fn create_default_plan(&self) -> ResultadoElap<BenefitsPlan> {
        let eps = self
            .get_providers_by_type(&ProviderType::EPS)
            .first()
            .cloned()
            .ok_or(ElapError::NotFound("EPS no disponible".to_string()))?;

        let pension = self
            .get_providers_by_type(&ProviderType::Pension)
            .first()
            .cloned()
            .ok_or(ElapError::NotFound("Pensión no disponible".to_string()))?;

        let arl = self
            .get_providers_by_type(&ProviderType::ARL)
            .first()
            .cloned()
            .ok_or(ElapError::NotFound("ARL no disponible".to_string()))?;

        let compensation = BenefitsProvider {
            name: "Colsubsidio".to_string(),
            provider_type: ProviderType::Compensation,
            contact: "info@colsubsidio.com.co".to_string(),
            coverage_percentage: 100.0,
        };

        Ok(BenefitsPlan {
            plan_name: "Plan Estándar Andina Foods".to_string(),
            eps,
            pension,
            arl,
            compensation,
            annual_cost: 0.0,
        })
    }
}

impl Default for BenefitsPlugin {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_benefits_plugin_new() {
        let plugin = BenefitsPlugin::new();
        assert!(plugin.enabled);
        assert!(!plugin.providers.is_empty());
    }

    #[test]
    fn test_calculate_severance() {
        let plugin = BenefitsPlugin::new();
        let severance = plugin.calculate_severance(3_000_000.0, 12).unwrap();
        assert!(severance > 0.0);
    }

    #[test]
    fn test_calculate_annual_bonus() {
        let plugin = BenefitsPlugin::new();
        let bonus = plugin.calculate_annual_bonus(3_000_000.0, 12).unwrap();
        assert!(bonus > 0.0);
    }

    #[test]
    fn test_calculate_vacation_days() {
        let plugin = BenefitsPlugin::new();
        let days = plugin.calculate_vacation_days(12);
        assert_eq!(days, 15); // 1 año = 15 días
    }

    #[test]
    fn test_calculate_total_benefits() {
        let plugin = BenefitsPlugin::new();
        let benefits = plugin
            .calculate_total_benefits(3_000_000.0, 24)
            .unwrap();

        assert!(benefits.severance > 0.0);
        assert!(benefits.annual_bonus > 0.0);
        assert!(benefits.vacation_days > 0);
    }

    #[test]
    fn test_get_providers_by_type() {
        let plugin = BenefitsPlugin::new();
        let eps_providers = plugin.get_providers_by_type(&ProviderType::EPS);
        assert!(!eps_providers.is_empty());
    }

    #[test]
    fn test_create_default_plan() {
        let plugin = BenefitsPlugin::new();
        let plan = plugin.create_default_plan().unwrap();
        assert!(!plan.plan_name.is_empty());
    }

    #[test]
    fn test_zero_salary_validation() {
        let plugin = BenefitsPlugin::new();
        let result = plugin.calculate_severance(0.0, 12);
        assert!(result.is_err());
    }
}
