use std::sync::Arc;

use axum::{extract::State, Json};
use serde::{Deserialize, Serialize};
use tokio::sync::Mutex;

use crate::data::gamedata::{Attribute, Beliefs, Facet, Goal, HappinessLevel, HealthInfo, Knowledge, Need, Profession, Skill, SubThoughts, UnitEmotion, UnitLabor, UnitThoughts};
use crate::dwarf::dwarf::Dwarf;
use crate::dfinstance::DFInstance;

#[derive(Clone)]
pub struct AppState {
    pub df: Arc<Mutex<DFInstance>>,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum GameDataResponse {
    Attributes      (Vec<Attribute>),
    Beliefs         (Vec<Beliefs>),
    Traits          (Vec<Facet>),
    Goals           (Vec<Goal>),
    HappinessLevels (Vec<HappinessLevel>),
    HealthInfo      (Vec<HealthInfo>),
    Knowledge       (Vec<Knowledge>),
    Labors          (Vec<UnitLabor>),
    Needs           (Vec<Need>),
    Skills          (Vec<Skill>),
    Emotions        (Vec<UnitEmotion>),
    Professions     (Vec<Profession>),
    Thoughts        (Vec<UnitThoughts>),
    Subthoughts     (Vec<SubThoughts>),
    None

}

/// get_gamedata_handler allows the GUI to request game data from the
/// server so we don't have to send it all with every request.
pub async fn get_gamedata_handler(State(state): State<AppState>) -> Json<Vec<GameDataResponse>> {
    let game_data = state.df.lock().await.game_data.clone();

    Json(vec![
        GameDataResponse::Attributes(game_data.attributes),
        GameDataResponse::Beliefs(game_data.beliefs),
        GameDataResponse::Traits(game_data.facets),
        GameDataResponse::Goals(game_data.goals),
        GameDataResponse::HappinessLevels(game_data.happiness_levels),
        GameDataResponse::HealthInfo(game_data.health_info),
        GameDataResponse::Knowledge(game_data.knowledge),
        GameDataResponse::Labors(game_data.labors),
        GameDataResponse::Needs(game_data.needs),
        GameDataResponse::Skills(game_data.skills),
        GameDataResponse::Emotions(game_data.unit_emotions),
        GameDataResponse::Professions(game_data.professions),
        GameDataResponse::Thoughts(game_data.unit_thoughts),
        GameDataResponse::Subthoughts(game_data.unit_subthoughts),
        GameDataResponse::None
    ])
}

pub async fn get_dwarves_handler(State(state): State<AppState>) -> Json<Vec<Dwarf>> {
    let df = state.df.lock().await;
    Json(df.dwarves.clone())
}