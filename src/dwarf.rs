#![allow(dead_code)]
pub mod dwarf {
    use std::collections::HashMap;
    use std::fmt::Error;

    use crate::squad::Squad;
    use crate::syndromes::Syndrome;
    use crate::time::DfTime;
    use crate::caste::caste::Caste;
    use crate::gamedata::*;
    use crate::histfigure::HistoricalFigure;
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
        pub histfig: HistoricalFigure,
        pub turn_count: i32,
        pub states: HashMap<i16, i32>,

        pub race: Race,
        pub caste: Caste,
        pub souls: Vec<usize>,
        pub _birth_date: (u64, u64),
        pub birth_date: DfTime,
        pub real_birth_date: DfTime,
        pub age: DfTime,
        pub arrival_time: DfTime,

        // TODO: FIX NAMES
        pub first_name: String,
        pub nickname: String,
        pub last_name: String,
        pub translated_last_name: String,
        pub nice_name: String,
        pub real_name: String,
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
        pub personality_addr: usize,
        pub emotions: Vec<UnitEmotion>,
        pub thoughts: Vec<i32>,
        pub stress_level: i32,
        pub happiness_level: HappinessLevel,
        pub mood: Mood,
        pub locked_mood: bool,
        pub syndromes: Vec<Syndrome>,

        pub squad: Squad,
        pub pending_squad_id: i32,
        pub pending_squad_position: i32,
        pub pending_squad_name: String,
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
            d.read_profession(df);
            d.read_age(df);
            d.read_historical_figure(df);
            d.read_fake_identity();
            // TODO: adult/non_citizen filters
            d.read_squad(df);
            // TODO: squad info
            // TODO: current job
            // TODO: labors
            // TODO: uniform
            // TODO: syndromes
            d.read_syndromes(df);
            // TODO: body size
            // TODO: curse
            // TODO: noble position
            d.read_soul(df);
            d.read_mood(df);
            d.read_emotions(df);
            d.read_beliefs(df);
            d.read_traits(df);
            d.read_goals(df);
            d.read_gender_orientation(df);
            // TODO: animal type
            // TODO: preferences

            Ok(d)
        }

        unsafe fn read_syndromes(&mut self, df: &DFInstance) {
            let syndromes_addr = self.addr + df.memory_layout.field_offset(MemorySection::Dwarf, "active_syndrome_vector");
            let syndromes = enum_mem_vec(&df.proc.handle, syndromes_addr);

            let mut is_cursed = false;
            for s in syndromes {
                let syn = Syndrome::new(df, s);
                let display_name = syn.clone().display_name().to_lowercase();
                if display_name.contains("vampcurse") {
                    is_cursed = true;
                }

                if syn.has_transform == true {
                    let race_id = syn.transform_race;
                    if race_id >= 0 {
                        let trans_race = df.races.iter().find(|&x| x.id == race_id).unwrap();
                        // TODO: crazed night creature
                    }



                } else if display_name.contains("werecurse") {
                    // TODO: werebeast
                }

                self.syndromes.push(syn);

            }

        }

        unsafe fn read_squad(&mut self, df: &DFInstance) {
            let squad_id = read_field::<i32>(&df.proc, self.addr, &df.memory_layout, MemorySection::Dwarf, "squad_id").unwrap();
            let squad_position = read_field::<i32>(&df.proc, self.addr, &df.memory_layout, MemorySection::Dwarf, "squad_position").unwrap();
            self.pending_squad_position = squad_position;

            if squad_id >= 0 {// && animal, adult
                let s = df.squads.iter().find(|&x| x.id == squad_id).unwrap();
                if s.id != 0 {
                    self.squad = s.clone();
                }
            }
        }

        unsafe fn read_age(&mut self, df: &DFInstance) {
            self._birth_date.0 = read_field::<i32>(&df.proc, self.addr, &df.memory_layout, MemorySection::Dwarf, "birth_year").unwrap() as u64;
            self._birth_date.1 = read_field::<i32>(&df.proc, self.addr, &df.memory_layout, MemorySection::Dwarf, "birth_time").unwrap() as u64;
            self.birth_date = DfTime::from_years(self._birth_date.0).add(self._birth_date.1);
            self.age = df.current_time().sub(self.birth_date.to_seconds());
            self.arrival_time = df.current_time().sub(self.turn_count as u64);
        }

        unsafe fn read_historical_figure(&mut self, df: &DFInstance) {
            if df.historical_figures.contains_key(&self.histfig_id) {
                self.histfig = HistoricalFigure::new(df, self.histfig_id);
            }
        }

        unsafe fn read_fake_identity(&mut self) {
            if self.histfig.has_fake_identity {
                self.real_name = self.nice_name.clone();
                self.real_birth_date = self.birth_date;

                self.first_name = self.histfig.fake_identity.fake_name.clone();
                self.nickname = self.histfig.fake_identity.fake_nickname.clone();
                let fake_birth_year = DfTime::from_years(self.histfig.fake_identity.fake_birth_year as u64);
                self.birth_date = fake_birth_year.add(self.histfig.fake_identity.fake_birth_time as u64);
                // TODO: last name
            }
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
        }

        unsafe fn read_soul(&mut self, df: &DFInstance) {
            self.souls = enum_mem_vec(&df.proc.handle, self.addr + df.memory_layout.field_offset(MemorySection::Dwarf, "souls"));
            if self.souls.len() > 1 {
                println!("Dwarf has more than one soul");
            }
            // get personality from the first soul
            self.personality_addr = self.souls[0] + df.memory_layout.field_offset(MemorySection::Soul, "personality");
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

        pub unsafe fn read_beliefs(&mut self, df: &DFInstance) {
            let beliefs_vec  = enum_mem_vec(&df.proc.handle, self.personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "beliefs"));
            for addr in beliefs_vec {
                let belief_id = read_mem::<i32>(&df.proc.handle, addr);
                if belief_id >= 0 {
                    let b = df.game_data.beliefs[belief_id as usize].clone();
                    let val = read_mem::<i16>(&df.proc.handle, addr + 0x4);
                    self.beliefs.push((b, val));
                }
            }
        }

        pub unsafe fn read_traits(&mut self, df: &DFInstance) {
            let traits_addr = self.personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "traits");
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
            let mut combat_hardened = read_mem::<i16>(&df.proc.handle, self.personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "combat_hardened"));
            combat_hardened = ((combat_hardened*(90-40)) / 100) + 40;
            let combat_hardened_trait = Facet{
                id: 0,
                name: "Combat Hardened".to_string(),
                ..Default::default()
            };
            self.traits.push((combat_hardened_trait, combat_hardened));

            // TODO: cave adapt/other special traits

        }

        pub unsafe fn read_goals(&mut self, df: &DFInstance) {
            let goals_addr =  self.personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "goals");
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
            let emotions_addr = self.personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "emotions");
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
                self.read_happiness_level(df);
                self.check_trauma(df); // lol I know that feel
            }
        }

        pub unsafe fn read_happiness_level(&mut self, df: &DFInstance) {
            let stress_level_addr = self.personality_addr + df.memory_layout.field_offset(MemorySection::Soul, "stress_level");
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

        pub unsafe fn check_trauma(&mut self, df: &DFInstance) {
            if self.mood == Mood::Trauma {
                let stress_msg = "has been overthrown by the stresses of day-to-day living";
                self.emotions.insert(0, UnitEmotion{
                    emotion: stress_msg.to_string(),
                    color: 0,
                    divider: 0,
                });
                println!("{} {}", self.first_name, stress_msg);
            }
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
            if mood != Mood::None && (
                mood == Mood::Beserk ||
                mood == Mood::Insane ||
                mood == Mood::Melancholy ||
                mood == Mood::Trauma
            ) || (mood_id >= 0 && mood_id <= 4) {
                self.locked_mood = true;
            }
            self.mood = mood;
        }

    }

    #[derive(Default, Debug, PartialEq, Clone)]
    pub enum Mood {
        #[default]
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