use serde::{Deserialize, Serialize};

use crate::{win::memory::memory::{enum_mem_vec, read_mem}, DFInstance, util::memory::read_mem_as_string, data::memorylayout::OffsetSection};

#[derive(Default, Clone, Serialize, Deserialize)]
pub struct Syndrome {
    pub addr: usize,
    pub id: i32,
    pub name: String,
    pub is_sickness: u8,
    pub has_transform: bool,
    pub transform_race: i32,
    pub class_names: Vec<String>,
}

impl Syndrome {
    pub unsafe fn new(df: &DFInstance, id_addr: usize) -> Syndrome {
        let id = read_mem::<i32>(&df.proc.handle, id_addr);
        let addr = *df.syndromes_vector.get(id as usize).unwrap();

        let mut s = Syndrome {
            addr,
            id,
            name: read_mem_as_string(&df.proc, addr),
            is_sickness: read_mem::<u8>(&df.proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "syn_sick_flag")),
            ..Default::default()
        };

        let syn_classes = enum_mem_vec(&df.proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Syndrome, "syn_classes_vector"));
        for c in syn_classes {
            let class_name = read_mem_as_string(&df.proc, c);
            // TODO: trim class names
            s.class_names.push(class_name);
        };

        let effects = enum_mem_vec(&df.proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Syndrome, "cie_effects"));
        for e in effects {
            let vtable_addr = read_mem::<usize>(&df.proc.handle, e);
            let vtable = read_mem::<usize>(&df.proc.handle, vtable_addr);
            let effect_type = read_mem::<i32>(&df.proc.handle, vtable + 0x1);
            let end = read_mem::<i32>(&df.proc.handle, e + df.memory_layout.field_offset(OffsetSection::Syndrome, "cie_end"));

            match effect_type {
                25 =>  {
                    // TODO: attribute change
                },
                26 => {
                    // TODO: attribute change
                },
                24 => {
                    // TODO: transformation
                },
                _ => {
                    s.name = "???".to_string();
                }
            }
        }
        s
    }

    pub unsafe fn display_name(self) -> String {
        let mut name = "???".to_string();

        if self.class_names.len() > 0 {
            name = self.class_names.join(", ");
            return format!("{}: {}", self.name, name);
        }
        name
    }

}

#[derive(Default, Serialize, Deserialize)]
pub struct Curse {
    pub name: String,
    pub curse_type: CurseType,
}

#[derive(Default, Serialize, Deserialize)]
pub enum CurseType {
    #[default]
    None = -1,
    Vampire = 0,
    Werebeast = 1,
    Other = 2
}