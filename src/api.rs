use std::sync::Arc;

use axum::{extract::State, Json};
use tokio::sync::Mutex;

use crate::dwarf::dwarf::Dwarf;
use crate::dfinstance::DFInstance;

#[derive(Clone)]
pub struct AppState {
    pub df: Arc<Mutex<DFInstance>>,
}

/// get_gamedata_handler allows the GUI to request game data from the
/// server so we don't have to send it all with every request.
pub async fn get_gamedata_handler(State(state): State<AppState>) -> Json<serde_json::Value> {
    let game_data = state.df.lock().await.game_data.clone();

    let response = serde_json::json!({
        "attributes": game_data.attributes,
        "beliefs": game_data.beliefs,
        "traits": game_data.facets,
        "goals": game_data.goals,
        "happiness_levels": game_data.happiness_levels,
        "health_info": game_data.health_info,
        "knowledge": game_data.knowledge,
        "labors": game_data.labors,
        "needs": game_data.needs,
        "skills": game_data.skills,
        "emotions": game_data.unit_emotions,
        "professions": game_data.professions,
        "thoughts": game_data.unit_thoughts,
        "subthoughts": game_data.unit_subthoughts,
    });

    Json(response)
}

pub async fn get_dwarves_handler(State(state): State<AppState>) -> Json<Vec<Dwarf>> {
    let df = state.df.lock().await;
    Json(df.dwarves.clone())
}