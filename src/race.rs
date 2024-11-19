pub mod race {
    use std::fmt::Error;
    use serde::{Deserialize, Serialize};

    use crate::items::material::Material;
    use crate::DFInstance;
    use crate::caste::caste::Caste;
    use crate::data::memorylayout::OffsetSection;
    use crate::flagarray::FlagArray;
    use crate::util::{capitalize_each, memory::read_mem_as_string};
    use crate::win::{memory::memory::enum_mem_vec, process::Process};

    #[derive(Default, Debug, Clone, Serialize, Deserialize)]
    pub struct Race {
        pub id: i32,
        pub name: String,
        pub plural_name: String,
        pub adjective: String,
        pub baby_name: String,
        pub baby_name_plural: String,
        pub child_name: String,
        pub child_name_plural: String,

        pub castes: Vec<Caste>,
        pub pref_strings: Vec<String>,
        pub flags: FlagArray,

        pub pop_ratio_vector: usize,
        pub materials_vector: Vec<usize>,
        pub tissues_vector: usize,

        pub creature_mats: Vec<Material>,
    }

    impl Race {
        pub unsafe fn new(df: &DFInstance, proc: &Process, id: i32, base_addr: usize) -> Result<Self, Error> {
            let mut r = Race {
                id,
                name:               read_mem_as_string(&proc, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "name_singular")),
                plural_name:        read_mem_as_string(&proc, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "name_plural")),
                adjective:          read_mem_as_string(&proc, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "adjective")),
                child_name:         read_mem_as_string(&proc, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "child_name_singular")),
                child_name_plural:  read_mem_as_string(&proc, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "child_name_plural")),
                baby_name:          read_mem_as_string(&proc, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "baby_name_singular")),
                baby_name_plural:   read_mem_as_string(&proc, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "baby_name_plural")),
                ..Default::default()
            };

            // TODO: implement these?
            r.pop_ratio_vector = df.memory_layout.field_offset(OffsetSection::Race, "pop_ratio_vector");
            r.materials_vector = enum_mem_vec(&proc.handle, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "materials_vector"));
            r.tissues_vector   = df.memory_layout.field_offset(OffsetSection::Race, "tissues_vector");

            r.pref_strings = enum_mem_vec(&proc.handle, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "pref_string_vector"))
                .iter()
                .map(|&p| read_mem_as_string(&proc, p))
                .collect();

            r.castes = enum_mem_vec(&proc.handle, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "castes_vector"))
                .iter()
                .map(|&c| Caste::new(df, proc, c))
                .collect();

            if r.id == df.dwarf_race_id{
                // TODO: caste ratios
            }

            r.flags = FlagArray::new(proc, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "flags"));
            r.fix_child_names();
            Ok(r)
        }

        unsafe fn fix_child_names(&mut self) {
            // if the baby name is empty, use the child name
            if self.baby_name.is_empty() && !self.child_name.is_empty() {
                self.baby_name = self.child_name.clone();
                self.baby_name_plural = self.child_name_plural.clone();
            // if the child name is empty, use the baby name
            } else if self.child_name.is_empty() && !self.baby_name.is_empty() {
                self.child_name = self.baby_name.clone();
                self.child_name_plural = self.baby_name_plural.clone();
            // if both are
            } else {
                self.baby_name = self.name.clone() + " Baby";
                self.baby_name_plural = self.plural_name.clone() + " Babies";
                self.child_name = self.name.clone() + " Offspring";
                self.child_name_plural = self.plural_name.clone() + " Offspring";
            }

            // capitalize
            self.child_name = capitalize_each(&self.child_name);
            self.child_name_plural = capitalize_each(&self.child_name_plural);
            self.baby_name = capitalize_each(&self.baby_name);
            self.baby_name_plural = capitalize_each(&self.baby_name_plural);
        }

        pub unsafe fn load_materials(&mut self, df: &DFInstance, proc: &Process) {
            if self.materials_vector.is_empty() {
                return;
            }

            self.creature_mats = self.materials_vector.iter()
                .enumerate()
                .map(|(i, &m)| Material::new(df, proc, i, m, true))
                .collect();
        }

    }
}