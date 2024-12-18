mod api;
mod attribute;
mod dfinstance;
mod dwarf;
mod caste;
mod thought;
mod flagarray;
mod language;
mod need;
mod win;
mod histfigure;
mod skill;
mod squad;
mod time;
mod syndromes;
mod items;
mod preference;
mod data;
mod race;
mod util;

use std::sync::Arc;
use axum::{routing::get, Router};
use tokio::sync::Mutex;

use dfinstance::{DFInstance, get_df_instance};
use api::{AppState, get_dwarves_handler, get_gamedata_handler};

#[tokio::main(flavor = "multi_thread", worker_threads = 2)]
async fn main() {
    unsafe {
        let state = AppState {
            df: Arc::new(Mutex::new(get_df_instance())),
        };

        let server = tokio::spawn({
            let state = state.clone();
            async move {
                let rest = Router::new()
                    .route("/data", get(get_gamedata_handler))
                    .route("/dwarves", get(get_dwarves_handler))
                    .with_state(state.clone());

                let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
                axum::serve(listener, rest).await.unwrap();
            }
        });

        let update_task = tokio::spawn(async move {
                loop {
                    // I think since I'm not using state after a move, I don't need to clone it
                    // and it will update the original state correctly for the server to use. ::fingers_crossed::
                    let mut df = state.df.lock().await;
                    // df.update();
                    println!("Updating...");
                    tokio::time::sleep(std::time::Duration::from_secs(60)).await;
                }
            });

        tokio::select! {
            _ = server => {},
            _ = update_task => {},
            _ = tokio::signal::ctrl_c() => {
                println!("Shutting down...");
            },
        }
    }
}
