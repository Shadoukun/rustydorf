#![allow(dead_code)]
pub mod dwarf {
    use std::collections::HashMap;
    use std::fmt::Error;

    use crate::caste::caste::Caste;
    use crate::gamedata::*;
    use crate::race::race::Race;
    use crate::win::memory::memory::enum_mem_vec;
    use crate::win::memory::memory::read_mem;
    use crate::{util::memory::{read_field, read_mem_as_string}, types::memorylayout::MemorySection, DFInstance};

    #[derive(Default)]
    pub struct Dwarf {
        pub addr: usize,
        pub id: i32,
        pub raw_prof_id: u8,
        pub histfig_id: i32,
        pub turn_count: i32,
        pub states: HashMap<i16, i32>,

        pub race: Race,
        pub caste: Caste,
        pub souls: Vec<usize>,

        pub first_name: String,
        pub nickname: String,
        pub last_name: String,
        pub translated_last_name: String,
        pub nice_name: String,
        pub translated_name: String,

        pub sex: Sex,
        pub orient_vec: Vec<Commitment>,
        pub orientation: Orientation,

        pub profession: Profession,
        pub custom_profession_name: String,

        pub beliefs: Vec<(Beliefs, i16)>,
        pub traits: Vec<(Facet, i16)>,
        pub goals: Vec<(Goal, i16)>,
        pub goals_realized: i32,

        pub emotions: Vec<UnitEmotion>,
        pub thoughts: Vec<i32>,

        pub squad_id: i32,
        pub squad_position: i32,
        pub pending_squad_id: i32,
        pub pending_squad_position: i32,
        pub pending_squad_name: String,



        // Happiness
        happiness_level: HappinessLevel,
        stress_level: i32,
        // Mood

    }

    impl Dwarf {
        pub unsafe fn new(df: &DFInstance, addr: usize) -> Result<Dwarf, Error> {
            let mut d = Dwarf{
                addr,
                id: read_field::<i32>(&df.proc, addr, &df.memory_layout, MemorySection::Dwarf, "id")?,
                ..Default::default()
            };

            // read race/caste before anything else to filter out non-dwarves
            d.read_race_and_caste(df)?;

            d.raw_prof_id = read_field::<u8>(&df.proc, addr, &df.memory_layout, MemorySection::Dwarf, "profession")?;
            d.histfig_id = read_field::<i32>(&df.proc, addr, &df.memory_layout, MemorySection::Dwarf, "hist_id")?;
            d.turn_count = read_field::<i32>(&df.proc, addr, &df.memory_layout, MemorySection::Dwarf, "turn_count")?;

            d.read_names(df);
            d.read_states(df);
            d.read_soul(df);
            d.read_personality(df);
            d.read_emotions(df);
            // TODO: age and migration
            d.read_profession(df);
            // TODO: profession

            // TODO: adult/non_citizen filters

            // TODO: fake identities
            // TODO: squad info
            // d.read_dwarf_gender_orientation(df);
            // TODO: profession
            // d.read_dwarf_mood(df);
            // TODO: labors
            println!("Name: {}", d.first_name);
            println!("Profession: {}", d.profession.name);
            for b in d.beliefs.iter() {
                println!("Belief: {:?} | Value: {}", b.0.name, b.1);
            }

            // for t in d.traits.iter() {
            //     println!("Trait: {:?} | Value: {}", t.0.name, t.1);
            // }

            for g in d.goals.iter() {
                println!("Goal: {:?} | Value: {}", g.0.name, g.1);
            }
            println!("\n");
            Ok(d)

        }

        unsafe fn read_gender_orientation(&mut self, df: &DFInstance) {
            let orient_offset = self.souls[0] + df.memory_layout.field_offset(MemorySection::Soul, "orientation");
            let orientation_byte = read_mem::<u8>(&df.proc.handle, orient_offset);

            let sex = Sex::from(read_field::<u8>(&df.proc, self.addr, &df.memory_layout, MemorySection::Dwarf, "sex").unwrap());

            let male_interest = Commitment::from((orientation_byte & (3<<1))>>1);
            let female_interest = Commitment::from((orientation_byte & (3<<3))>>3);

            let mut orientation: Orientation = Default::default();

            if sex == Sex::Male {
                if male_interest != Commitment::Uninterested && female_interest != Commitment::Uninterested {
                    orientation = Orientation::Bisexual;
                } else if female_interest != Commitment::Uninterested {
                    orientation = Orientation::Heterosexual;
                } else if male_interest != Commitment::Uninterested {
                    orientation = Orientation::Homosexual;
                } else {
                    orientation = Orientation::Asexual;
                }

            } else if sex == Sex::Female {
                if female_interest != Commitment::Uninterested && male_interest != Commitment::Uninterested {
                    orientation = Orientation::Bisexual;
                } else if male_interest != Commitment::Uninterested {
                    orientation = Orientation::Heterosexual;
                } else if female_interest != Commitment::Uninterested {
                    orientation = Orientation::Homosexual;
                } else {
                    orientation = Orientation::Asexual;
                }
            }

            self.sex = sex;
            self.orientation = orientation;
            self.orient_vec = vec![male_interest, female_interest];

            println!("Sex: {:?}, ", self.sex);
            println!("Sexual Orientation: {:?} [Male Interest: {:?} | Female Interest: {:?}]", self.orientation, self.orient_vec[0], self.orient_vec[1]);
        }

        unsafe fn read_soul(&mut self, df: &DFInstance) {
            self.souls = enum_mem_vec(&df.proc.handle, self.addr + df.memory_layout.field_offset(MemorySection::Dwarf, "souls"));

            if self.souls.len() > 1 {
                println!("Dwarf has more than one soul");
            }
        }

        unsafe fn read_race_and_caste(&mut self, df: &DFInstance) -> Result<(), Error> {
            let race_id = read_field::<i32>(&df.proc, self.addr, &df.memory_layout, MemorySection::Dwarf, "race")?;
            let race = df.get_race(race_id).unwrap();
            if race.name != "dwarf" {
                return Err(Error);
            }

            // I'm pretty sure this doesn't work as intended but dwarves only have 2 castes so it doesn't matter for now
            let caste_id = read_field::<i32>(&df.proc, self.addr, &df.memory_layout, MemorySection::Dwarf, "caste")?;
            let caste: &Caste;
            if caste_id == 0 {
                caste = &race.castes[0];
            } else {
                caste = &race.castes[1];
            }

            // I think I only need to clone because I'm bad at lifetimes.
            self.race = race.clone();
            self.caste = caste.clone();
            Ok(())
        }

        unsafe fn read_states(&mut self, df: &DFInstance) {
            let states_vec = enum_mem_vec(&df.proc.handle, self.addr + df.memory_layout.field_offset(MemorySection::Dwarf, "states"));
            let mut states: HashMap<i16, i32> = HashMap::new();
            for s in states_vec {
                let k = read_mem::<i16>(&df.proc.handle, s);
                let v = read_mem::<i32>(&df.proc.handle, s + 0x4); // 0x4 or sizeof usize?
                states.insert(k, v);
            }
            self.states = states;
        }

        pub unsafe fn read_names(&mut self, df: &DFInstance) {
            let name_offset =  self.addr + df.memory_layout.field_offset(MemorySection::Dwarf, "name");
            self.first_name = read_mem_as_string(&df.proc, name_offset + df.memory_layout.field_offset(MemorySection::Word, "first_name"));
            self.nickname = read_mem_as_string(&df.proc, name_offset + df.memory_layout.field_offset(MemorySection::Word, "nickname"));
            // TODO: last_name
            self.last_name = "".to_string();
        }

        pub unsafe fn read_last_name(df: &DFInstance, offset: usize) -> String {
            df.languages.language_word(df, offset)
        }

        pub unsafe fn read_profession(&mut self, df: &DFInstance) {
            let prof = df.game_data.professions.iter().find(|&x| x.id == self.raw_prof_id as i32).unwrap();
            self.profession = prof.clone();
            // TODO: custom profession
        }

        pub unsafe fn read_personality(&mut self, df: &DFInstance) {
            let personality_addr = self.souls[0] + df.memory_layout.field_offset(MemorySection::Soul, "personality");

            //
            // Beliefs
            //
            let beliefs_vec  = enum_mem_vec(&df.proc.handle, personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "beliefs"));
            for addr in beliefs_vec {
                let belief_id = read_mem::<i32>(&df.proc.handle, addr);
                if belief_id >= 0 {
                    let b = df.game_data.beliefs[belief_id as usize].clone();
                    let val = read_mem::<i16>(&df.proc.handle, addr + 0x4);
                    self.beliefs.push((b, val));
                }
            }

            //
            // Traits (Facets)
            //
            let traits_addr = personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "traits");
            for i in 0..df.game_data.facets.len() {
                let mut tr = df.game_data.facets[i].clone();
                let val = read_mem::<i16>(&df.proc.handle, traits_addr + i * 2);

                // make trait id the index if it's not set
                if tr.id == 0 {
                    tr.id = i as i32;
                }

                // trait belief conflicts. no idea if this works.
                for conflict in tr.clone().belief_conflicts {
                    let belief = df.game_data.beliefs[conflict.1 as usize].clone();
                    if let Some(b) = self.beliefs.iter_mut().find(|x| x.0 == belief) {
                        if (b.1 > 10 && val < 40 ) || (b.1 < -10 && val > 60) {
                            b.0.trait_conflicts.push(conflict.1);
                        }
                    }
                }
                self.traits.push((tr, val));
            }

            // special traits
            let mut combat_hardened = read_mem::<i16>(&df.proc.handle, personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "combat_hardened"));
            combat_hardened = ((combat_hardened*(90-40)) / 100) + 40;
            let combat_hardened_trait = Facet{
                id: 0,
                name: "Combat Hardened".to_string(),
                ..Default::default()
            };
            self.traits.push((combat_hardened_trait, combat_hardened));
            // TODO: cave adapt/other special traits

            //
            // Goals
            //
            let goals_addr =  personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "goals");
            let goals = enum_mem_vec(&df.proc.handle, goals_addr);
            for addr in goals {
                let goal_type = read_mem::<i32>(&df.proc.handle, addr + 0x4);
                if goal_type >= 0 {
                    let goal = df.game_data.goals.iter().find(|&x| x.id == goal_type).unwrap().clone();
                    let val = read_mem::<i16>(&df.proc.handle, addr + df.memory_layout.field_offset(MemorySection::Soul, "goal_realized"));
                    // TODO: vampire goals
                    if val > 0 { self.goals_realized += 1; };
                    self.goals.push((goal, val));
                }
            }
        }

        pub unsafe fn read_emotions(&mut self, df: &DFInstance) {
            let personality_addr = self.souls[0] + df.memory_layout.field_offset(MemorySection::Soul, "personality");
            let emotions_addr = personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "emotions");
            for e in enum_mem_vec(&df.proc.handle, emotions_addr) {
                let emotion_type = read_mem::<i32>(&df.proc.handle, e + df.memory_layout.field_offset(MemorySection::Emotion, "emotion_type"));
                let thought_id = read_mem::<i32>(&df.proc.handle, e + df.memory_layout.field_offset(MemorySection::Emotion, "thought_id"));
                println!("Emotion Type: {}", emotion_type);

                if !self.thoughts.contains(&thought_id) {
                    self.emotions.push(df.game_data.unit_emotions[emotion_type as usize].clone());
                }

                // TODO: sort in descending order
                if thought_id >= 0 {
                    self.thoughts.push(thought_id);
                }

                for e in self.emotions.iter() {
                    println!("Emotion: {:?}", e.emotion);
                }
                println!("\nThoughts: ");
                for t in self.thoughts.iter() {
                    println!("{:?}", df.game_data.unit_thoughts[*t as usize - 1]);
                }

                // TODO: stress effects

                // TODO: dated emotions
                self.read_happiness_level(df, personality_addr);
            }
        }

        pub unsafe fn read_happiness_level(&mut self, df: &DFInstance, personality_addr: usize) {
            let stress_level_addr = personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "stress_level");
            self.stress_level = read_mem::<i32>(&df.proc.handle, stress_level_addr);
            let mut happiness_level = df.game_data.happiness_levels[0].clone();
            for h in &df.game_data.happiness_levels {
                if (self.stress_level - h.threshold).abs() < (self.stress_level - happiness_level.threshold).abs() {
                    happiness_level = h.clone();
                }
            }
            println!("Stress Level: {:?}", happiness_level);
            self.happiness_level = happiness_level;
    }
        pub unsafe fn read_mood(&mut self, df: &DFInstance) {
            let mood_id = read_field::<i16>(&df.proc, self.addr, &df.memory_layout, MemorySection::Dwarf, "mood").unwrap();
            let mut mood = Mood::from(mood_id);
            let temp_mood_offset = df.memory_layout.field_offset(MemorySection::Dwarf, "temp_mood");

            if mood == Mood::None {
                let temp_mood = read_mem::<i16>(&df.proc.handle, self.addr + temp_mood_offset);
                if temp_mood != -1 {
                    mood = Mood::from(10 + temp_mood);
                }
            }

            // ignore babies
            if mood == Mood::Baby {
                mood = Mood::None;
            }

            //check if they've had a mood/artifact if they're not currently in a craft-type mood
            if mood == Mood::None || mood_id > 4 {
                // todo!();
            }

            // this feels bad
            let mut locked_mood = false;
            if mood != Mood::None && (
                mood == Mood::Beserk ||
                mood == Mood::Insane ||
                mood == Mood::Melancholy ||
                mood == Mood::Trauma
            ) || (mood_id >= 0 && mood_id <= 4) {
                locked_mood = true;
            }

            println!("Mood: {:?} | Locked Mood: {}", mood, locked_mood);
        }


    }

    #[derive(Debug, PartialEq, Clone)]
    pub enum Mood {
        None = -1,
        Fey,
        Secret,
        Possessed,
        Macabre,
        Fell,
        Melancholy,
        Insane,
        Beserk,
        Baby,
        Trauma,
        Martial,
        Enraged,
        Tantrum,
        Depressed,
        Oblivious
    }

    impl From<i16> for Mood {
        fn from(value: i16) -> Self {
            match value {
                0 => Mood::Fey,
                1 => Mood::Secret,
                2 => Mood::Possessed,
                3 => Mood::Macabre,
                4 => Mood::Fell,
                5 => Mood::Melancholy,
                6 => Mood::Insane,
                7 => Mood::Beserk,
                8 => Mood::Baby,
                9 => Mood::Trauma,
                10 => Mood::Martial,
                11 => Mood::Enraged,
                12 => Mood::Tantrum,
                13 => Mood::Depressed,
                14 => Mood::Oblivious,
                _ => Mood::None,
            }
        }
    }



    #[derive(Default, Debug, PartialEq)]
    pub enum Sex {
        #[default]
        Female = 0,
        Male = 1,
        Unknown = -1,
    }

    impl From<u8> for Sex {
        fn from(value: u8) -> Self {
            match value {
                0 => Sex::Female,
                1 => Sex::Male,
                _ => Sex::Unknown,
            }
        }
    }


    #[derive(Debug, PartialEq)]
    pub enum Commitment {
        Uninterested = 0,
        Lover = 1,
        Marriage = 2,
    }

    impl From<u8> for Commitment {
        fn from(value: u8) -> Self {
            match value {
                1 => Commitment::Lover,
                2 => Commitment::Marriage,
                _ => Commitment::Uninterested,
            }
        }
    }

    #[derive(Default, Debug, PartialEq)]
    pub enum Orientation {
        #[default]
        Heterosexual,
        Bisexual,
        Homosexual,
        Asexual,
    }
}