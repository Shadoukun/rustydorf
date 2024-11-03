pub mod race {
    use std::{fmt::Error, ops::Add};

    use serde::{Deserialize, Serialize};

    use crate::caste::caste::Caste;
    use crate::types::flagarray::FlagArray;
    use crate::win::{memory::memory::enum_mem_vec, process::Process};

    use crate::util::address_plus_offset;
    use crate::{capitalize_each, DFInstance};
    use crate::util::memory::{read_field_as_string, read_field_as_vec, read_mem_as_string};
    use crate::data::memorylayout::{MemoryOffsets, OffsetSection};

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

        pub pref_strings: Vec<String>,
        pub pop_ratio_vector: usize,
        pub castes_vector: usize,
        pub castes: Vec<Caste>,
        pub materials_vector: usize,
        pub tissues_vector: usize,

        pub flags: FlagArray,

    }

    impl Race {
        pub unsafe fn new(df: &DFInstance, proc: &Process, id: i32, base_addr: usize) -> Result<Self, Error> {
            let mut r: Race = Default::default();

            r.id = id;
            r.name = read_field_as_string(&proc, base_addr, &df.memory_layout, OffsetSection::Race, "name_singular")?;
            r.plural_name = read_field_as_string(&proc, base_addr, &df.memory_layout, OffsetSection::Race, "name_plural")?;
            r.adjective = read_field_as_string(&proc, base_addr, &df.memory_layout, OffsetSection::Race, "adjective")?;
            r.child_name = read_field_as_string(&proc, base_addr, &df.memory_layout, OffsetSection::Race, "child_name_singular")?;
            r.child_name_plural = read_field_as_string(&proc, base_addr, &df.memory_layout, OffsetSection::Race, "child_name_plural")?;
            r.baby_name = read_field_as_string(&proc, base_addr, &df.memory_layout, OffsetSection::Race, "baby_name_singular")?;
            r.baby_name_plural = read_field_as_string(&proc, base_addr, &df.memory_layout, OffsetSection::Race, "baby_name_plural")?;

            if r.baby_name.is_empty() && !r.child_name.is_empty() {
                r.baby_name = r.child_name.clone();
                r.baby_name_plural = r.child_name_plural.clone();
            }
            if r.child_name.is_empty() && !r.baby_name.is_empty() {
                r.child_name = r.baby_name.clone();
                r.child_name_plural = r.baby_name_plural.clone();
            }

            if r.baby_name.is_empty() {
                r.baby_name = r.name.clone() + " Baby";
                r.baby_name_plural = r.plural_name.clone() + " Babies";
            }

            if r.child_name.is_empty() {
                r.child_name = r.name.clone() + " Offspring";
                r.child_name_plural = r.plural_name.clone() + " Offspring";
            }

            r.child_name = capitalize_each(&r.child_name);
            r.child_name_plural = capitalize_each(&r.child_name_plural);
            r.baby_name = capitalize_each(&r.baby_name);
            r.baby_name_plural = capitalize_each(&r.baby_name_plural);

                let pref_string_vector_offset = df.memory_layout.field_offset(OffsetSection::Race, "pref_string_vector");
                let pref_strings = enum_mem_vec(&proc.handle, base_addr.add(pref_string_vector_offset));
                for p in pref_strings {
                    let pref_string = read_mem_as_string(&proc, p);
                    r.pref_strings.push(pref_string);
                }

            r.castes_vector = df.memory_layout.field_offset(OffsetSection::Race, "castes_vector");
            r.pop_ratio_vector = df.memory_layout.field_offset(OffsetSection::Race, "pop_ratio_vector");
            r.materials_vector = df.memory_layout.field_offset(OffsetSection::Race, "materials_vector");
            r.tissues_vector = df.memory_layout.field_offset(OffsetSection::Race, "tissues_vector");

            // load race castes
            let castes = enum_mem_vec(&proc.handle, base_addr.add(r.castes_vector));
            if !castes.is_empty() {
                for c in castes {
                    let caste = Caste::new(df, proc, c);
                    r.castes.push(caste);
                }
            }

            if r.id == df.dwarf_race_id{
                // todo: caste ratios
            }

            r.flags = FlagArray::new(&df, proc, base_addr + df.memory_layout.field_offset(OffsetSection::Race, "flags"));
            Ok(r)
        }
    }
}