//! RecruitmentPlugin - Gestión de procesos de contratación
//!
//! Plugin especializado para:
//! - Publicación de ofertas de empleo
//! - Gestión de candidatos
//! - Screening automático
//! - Onboarding de empleados

use serde::{Deserialize, Serialize};
use crate::error::{ElapError, ResultadoElap};

/// Información de oferta de empleo
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct JobPosting {
    pub id: String,
    pub title: String,
    pub department: String,
    pub salary_range: (f64, f64),
    pub description: String,
    pub requirements: Vec<String>,
    pub posted_date: String,
    pub status: JobStatus,
}

/// Estado de oferta
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum JobStatus {
    Open,
    Closed,
    Filled,
    OnHold,
}

/// Información de candidato
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Candidate {
    pub id: String,
    pub name: String,
    pub email: String,
    pub phone: String,
    pub position_applied: String,
    pub experience_years: u32,
    pub education_level: String,
    pub skills: Vec<String>,
    pub application_date: String,
    pub screening_score: Option<f32>,
}

/// Resultado de screening
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ScreeningResult {
    pub candidate_id: String,
    pub position_id: String,
    pub match_score: f32,  // 0.0 - 1.0
    pub strengths: Vec<String>,
    pub gaps: Vec<String>,
    pub recommendation: ScreeningRecommendation,
}

/// Recomendación de screening
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ScreeningRecommendation {
    StrongMatch,
    Potential,
    Review,
    NotRecommended,
}

/// Plan de onboarding
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OnboardingPlan {
    pub employee_id: String,
    pub employee_name: String,
    pub department: String,
    pub position: String,
    pub start_date: String,
    pub tasks: Vec<OnboardingTask>,
}

/// Tarea de onboarding
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OnboardingTask {
    pub description: String,
    pub due_date: String,
    pub owner: String,
    pub completed: bool,
}

/// RecruitmentPlugin
pub struct RecruitmentPlugin {
    pub enabled: bool,
    pub active_postings: Vec<JobPosting>,
    pub candidates: Vec<Candidate>,
}

impl RecruitmentPlugin {
    /// Crear nuevo RecruitmentPlugin
    pub fn new() -> Self {
        Self {
            enabled: true,
            active_postings: Vec::new(),
            candidates: Vec::new(),
        }
    }

    /// Crear oferta de empleo
    pub fn create_job_posting(
        &mut self,
        title: &str,
        department: &str,
        salary_min: f64,
        salary_max: f64,
        description: &str,
        requirements: Vec<String>,
    ) -> ResultadoElap<JobPosting> {
        if title.is_empty() || department.is_empty() {
            return Err(ElapError::ValidationError(
                "Título y departamento requeridos".to_string(),
            ));
        }

        if salary_max < salary_min || salary_min <= 0.0 {
            return Err(ElapError::ValidationError(
                "Rango salarial inválido".to_string(),
            ));
        }

        let job = JobPosting {
            id: format!("JOB_{}", chrono::Local::now().timestamp()),
            title: title.to_string(),
            department: department.to_string(),
            salary_range: (salary_min, salary_max),
            description: description.to_string(),
            requirements,
            posted_date: chrono::Local::now().to_string(),
            status: JobStatus::Open,
        };

        self.active_postings.push(job.clone());
        Ok(job)
    }

    /// Registrar candidato
    pub fn register_candidate(
        &mut self,
        name: &str,
        email: &str,
        phone: &str,
        position: &str,
        experience_years: u32,
        education_level: &str,
        skills: Vec<String>,
    ) -> ResultadoElap<Candidate> {
        if name.is_empty() || email.is_empty() {
            return Err(ElapError::ValidationError(
                "Nombre y email requeridos".to_string(),
            ));
        }

        let candidate = Candidate {
            id: format!("CAND_{}", chrono::Local::now().timestamp()),
            name: name.to_string(),
            email: email.to_string(),
            phone: phone.to_string(),
            position_applied: position.to_string(),
            experience_years,
            education_level: education_level.to_string(),
            skills,
            application_date: chrono::Local::now().to_string(),
            screening_score: None,
        };

        self.candidates.push(candidate.clone());
        Ok(candidate)
    }

    /// Hacer screening automático de candidato
    pub fn screen_candidate(
        &self,
        candidate: &Candidate,
        job: &JobPosting,
    ) -> ResultadoElap<ScreeningResult> {
        let mut match_score = 0.0;
        let mut strengths = Vec::new();
        let mut gaps = Vec::new();

        // Evaluar experiencia (40%)
        let experience_score = (candidate.experience_years as f32).min(15.0) / 15.0 * 0.4;
        match_score += experience_score;

        if candidate.experience_years >= 3 {
            strengths.push("Experiencia sólida".to_string());
        }

        // Evaluar educación (20%)
        let education_score = match candidate.education_level.as_str() {
            "Profesional" => 0.2,
            "Técnico" => 0.15,
            "Bachiller" => 0.1,
            _ => 0.0,
        };
        match_score += education_score;

        if education_score < 0.15 {
            gaps.push("Educación no óptima para el puesto".to_string());
        }

        // Evaluar skills (40%)
        let required_count = job.requirements.len();
        let matching_skills = candidate
            .skills
            .iter()
            .filter(|s| job.requirements.contains(s))
            .count();

        let skills_score = if required_count > 0 {
            (matching_skills as f32 / required_count as f32) * 0.4
        } else {
            0.4
        };

        match_score += skills_score;

        if matching_skills > required_count / 2 {
            strengths.push(format!("Posee {} de {} skills requeridos", matching_skills, required_count));
        } else {
            gaps.push(format!("Solo {} de {} skills requeridos", matching_skills, required_count));
        }

        // Determinar recomendación
        let recommendation = match match_score {
            s if s >= 0.8 => ScreeningRecommendation::StrongMatch,
            s if s >= 0.6 => ScreeningRecommendation::Potential,
            s if s >= 0.4 => ScreeningRecommendation::Review,
            _ => ScreeningRecommendation::NotRecommended,
        };

        Ok(ScreeningResult {
            candidate_id: candidate.id.clone(),
            position_id: job.id.clone(),
            match_score,
            strengths,
            gaps,
            recommendation,
        })
    }

    /// Crear plan de onboarding
    pub fn create_onboarding_plan(
        &self,
        employee_id: &str,
        employee_name: &str,
        department: &str,
        position: &str,
        start_date: &str,
    ) -> ResultadoElap<OnboardingPlan> {
        let tasks = vec![
            OnboardingTask {
                description: "Orientación general de la empresa".to_string(),
                due_date: start_date.to_string(),
                owner: "RRHH".to_string(),
                completed: false,
            },
            OnboardingTask {
                description: "Capacitación en políticas de seguridad".to_string(),
                due_date: format!("{} + 1 día", start_date),
                owner: "Seguridad".to_string(),
                completed: false,
            },
            OnboardingTask {
                description: "Entrenamiento específico del puesto".to_string(),
                due_date: format!("{} + 3 días", start_date),
                owner: department.to_string(),
                completed: false,
            },
            OnboardingTask {
                description: "Revisión de primer mes".to_string(),
                due_date: format!("{} + 30 días", start_date),
                owner: "Manager".to_string(),
                completed: false,
            },
        ];

        Ok(OnboardingPlan {
            employee_id: employee_id.to_string(),
            employee_name: employee_name.to_string(),
            department: department.to_string(),
            position: position.to_string(),
            start_date: start_date.to_string(),
            tasks,
        })
    }

    /// Obtener ofertas abiertas
    pub fn get_open_jobs(&self) -> Vec<&JobPosting> {
        self.active_postings
            .iter()
            .filter(|j| j.status == JobStatus::Open)
            .collect()
    }

    /// Contar candidatos por posición
    pub fn count_candidates_for_position(&self, position: &str) -> usize {
        self.candidates
            .iter()
            .filter(|c| c.position_applied.to_lowercase() == position.to_lowercase())
            .count()
    }
}

impl Default for RecruitmentPlugin {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_recruitment_plugin_new() {
        let plugin = RecruitmentPlugin::new();
        assert!(plugin.enabled);
        assert!(plugin.active_postings.is_empty());
    }

    #[test]
    fn test_create_job_posting() {
        let mut plugin = RecruitmentPlugin::new();
        let job = plugin
            .create_job_posting(
                "Senior Developer",
                "IT",
                4_000_000.0,
                6_000_000.0,
                "Buscamos desarrollador senior",
                vec!["Rust".to_string(), "Docker".to_string()],
            )
            .unwrap();

        assert_eq!(job.title, "Senior Developer");
        assert_eq!(job.status, JobStatus::Open);
    }

    #[test]
    fn test_register_candidate() {
        let mut plugin = RecruitmentPlugin::new();
        let candidate = plugin
            .register_candidate(
                "Juan García",
                "juan@email.com",
                "+57 123 456",
                "Senior Developer",
                5,
                "Profesional",
                vec!["Rust".to_string(), "Docker".to_string(), "Python".to_string()],
            )
            .unwrap();

        assert_eq!(candidate.name, "Juan García");
        assert_eq!(candidate.experience_years, 5);
    }

    #[test]
    fn test_screen_candidate() {
        let mut plugin = RecruitmentPlugin::new();

        let job = plugin
            .create_job_posting(
                "Senior Developer",
                "IT",
                4_000_000.0,
                6_000_000.0,
                "Buscamos desarrollador",
                vec!["Rust".to_string(), "Docker".to_string()],
            )
            .unwrap();

        let candidate = plugin
            .register_candidate(
                "Juan García",
                "juan@email.com",
                "+57 123 456",
                "Senior Developer",
                5,
                "Profesional",
                vec!["Rust".to_string(), "Docker".to_string()],
            )
            .unwrap();

        let result = plugin.screen_candidate(&candidate, &job).unwrap();
        assert!(result.match_score > 0.0);
    }

    #[test]
    fn test_create_onboarding_plan() {
        let plugin = RecruitmentPlugin::new();
        let plan = plugin
            .create_onboarding_plan(
                "EMP001",
                "Juan García",
                "IT",
                "Senior Developer",
                "2026-08-15",
            )
            .unwrap();

        assert_eq!(plan.employee_name, "Juan García");
        assert!(!plan.tasks.is_empty());
    }

    #[test]
    fn test_get_open_jobs() {
        let mut plugin = RecruitmentPlugin::new();
        plugin
            .create_job_posting(
                "Developer",
                "IT",
                3_000_000.0,
                5_000_000.0,
                "Job desc",
                vec![],
            )
            .unwrap();

        let open = plugin.get_open_jobs();
        assert_eq!(open.len(), 1);
    }

    #[test]
    fn test_invalid_salary_range() {
        let mut plugin = RecruitmentPlugin::new();
        let result = plugin.create_job_posting(
            "Developer",
            "IT",
            5_000_000.0,
            3_000_000.0, // max < min
            "Job desc",
            vec![],
        );
        assert!(result.is_err());
    }
}
