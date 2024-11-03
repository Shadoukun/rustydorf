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

fn main() {

    unsafe {
        let proc = Process::new_by_name("Dwarf Fortress.exe");
        // doesnt error correctly
        if proc.pid == 0 {
                panic!("Dwarf Fortress not found.");
        }

        let df = DFInstance::new(&proc);
    };
}