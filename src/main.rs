mod dfinstance;
mod dwarf;
mod caste;
mod types;
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

use dfinstance::DFInstance;
use win::process::Process;

unsafe fn get_df_instance() -> DFInstance {
    let proc = Process::new_by_name("Dwarf Fortress.exe");
    let df = DFInstance::new(&proc);
    df
}

// #[tokio::main]
fn main() {
    let df = unsafe { get_df_instance() };
}