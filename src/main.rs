mod dfinstance;
mod dwarf;
mod caste;
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

use std::sync::Arc;
use tokio::sync::Mutex;

use dfinstance::DFInstance;
use win::process::Process;

unsafe fn get_df_instance() -> DFInstance {
    let proc = Process::new_by_name("Dwarf Fortress.exe");
    let df = DFInstance::new(&proc);
    df
}

#[tokio::main]
async fn main() {
    unsafe {
        let df = Arc::new(Mutex::new(get_df_instance()));
    }

}