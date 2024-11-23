mod attribute;
mod dfinstance;
mod dwarf;
mod caste;
mod thought;
mod flagarray;
mod language;
mod win;
mod histfigure;
mod squad;
mod time;
mod syndromes;
mod items;
mod preference;
mod data;
mod race;
mod util;

use axum::{extract::{Path, State}, Json};
use data::gamedata::{Attribute, Beliefs, Facet, Profession, SubThoughts, UnitLabor, UnitThoughts};
use dwarf::dwarf::Dwarf;
use serde::{Deserialize, Serialize};

use std::sync::Arc;
use axum::{routing::get, Router};
use tokio::sync::Mutex;

use dfinstance::DFInstance;
use win::process::Process;

#[derive(Clone)]
struct AppState {
    df: Arc<Mutex<DFInstance>>,
}

#[derive(Debug, Serialize, Deserialize)]
enum GameDataResponse {
    Attributes(Vec<Attribute>),
    Labors(Vec<UnitLabor>),
    Professions(Vec<Profession>),
    Traits(Vec<Facet>),
    Thoughts(Vec<UnitThoughts>),
    Subthoughts(Vec<SubThoughts>),
    Beliefs(Vec<Beliefs>),
    None

}

unsafe fn get_df_instance() -> DFInstance {
    let proc = Process::new_by_name("Dwarf Fortress.exe");
    let df = DFInstance::new(&proc);
    println!("Dwarves: {}", df.dwarves.len());
    df
}

async fn get_dwarves_handler(State(state): State<AppState>) -> Json<Vec<Dwarf>> {
    let df = state.df.lock().await;
    Json(df.dwarves.clone())
}

/// get_gamedata_handler allows the GUI to request game data from the
/// server so we don't have to send it all with every request.
async fn get_gamedata_handler(State(state): State<AppState>, Path(name): Path<String>) -> Json<GameDataResponse> {
    let df = state.df.lock().await;

    let data= match name.as_str() {
        "attributes" =>  Json(GameDataResponse::Attributes(df.game_data.attributes.clone())),
        "beliefs" =>     Json(GameDataResponse::Beliefs(df.game_data.beliefs.clone())),
        "labors" =>      Json(GameDataResponse::Labors(df.game_data.labors.clone())),
        "professions" => Json(GameDataResponse::Professions(df.game_data.professions.clone())),
        "traits" =>      Json(GameDataResponse::Traits(df.game_data.facets.clone())),
        "thoughts" =>    Json(GameDataResponse::Thoughts(df.game_data.unit_thoughts.clone())),
        "subthoughts" => Json(GameDataResponse::Subthoughts(df.game_data.unit_subthoughts.clone())),
        _ => Json(GameDataResponse::None),
    };
    data
}

#[tokio::main]
async fn main() {
    unsafe {
        let state = AppState {
            df: Arc::new(Mutex::new(get_df_instance())),
        };

        let rest = Router::new()
        .route("/data/:name", get(get_gamedata_handler))
        .route("/dwarves", get(get_dwarves_handler))
        .with_state(state.clone());

        let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
        axum::serve(listener, rest).await.unwrap();
    }
}
