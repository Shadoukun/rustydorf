use serde::{Deserialize, Serialize};

use crate::DFInstance;
use crate::win::{memory::memory::read_mem, process::Process};
use crate::data::memorylayout::OffsetSection;

#[derive(Default, Debug, Clone, Serialize, Deserialize)]
pub struct Need {
    id: i32,
    name: String,
    deity_id: i32,
    focus_level: i32,
    need_level: i32,
    adjective: String,
    description: String,
    degree_adjective: String,
}

impl Need {
    pub unsafe fn new (df: &DFInstance, proc: &Process, address: usize) -> Self {
        Need {
            id: read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Need, "id")),
            deity_id: read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Need, "deity_id")),
            focus_level: read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Need, "focus_level")),
            need_level: read_mem::<i32>(&proc.handle, address + df.memory_layout.field_offset(OffsetSection::Need, "need_level")),
            ..Default::default()
        }
    }
}