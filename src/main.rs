mod dfinstance;
mod dwarf;
mod caste;
mod emotion;
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

use axum::{extract::State, Json};
use dwarf::dwarf::Dwarf;

use std::sync::Arc;
use axum::{routing::get, Router};
use tokio::sync::Mutex;

use dfinstance::DFInstance;
use win::process::Process;

unsafe fn get_df_instance() -> DFInstance {
    let proc = Process::new_by_name("Dwarf Fortress.exe");
    let df = DFInstance::new(&proc);
    println!("Dwarves: {}", df.dwarves.len());
    df
}

#[derive(Clone)]
struct AppState {
    df: Arc<Mutex<DFInstance>>,
}


#[tokio::main]
async fn main() {
    unsafe {
        let state = AppState {
            df: Arc::new(Mutex::new(get_df_instance())),
        };

        let rest = Router::new().route("/dwarves", get(get_dwarves_handler)).with_state(state.clone());
        let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
        axum::serve(listener, rest).await.unwrap();
    }
}


#[axum::debug_handler]
async fn get_dwarves_handler(State(state): State<AppState>) -> Json<Vec<Dwarf>> {
    let df = state.df.lock().await;
    Json(df.dwarves.clone())
}