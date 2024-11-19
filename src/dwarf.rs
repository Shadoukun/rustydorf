#![allow(dead_code)]
pub mod dwarf {
    use std::collections::HashMap;
    use std::fmt::Error;

    use serde::Deserialize;
    use serde::Serialize;

    use crate::thought::Thought;
    use crate::histfigure::FortressPosition;
    use crate::preference::Commitment;
    use crate::preference::Orientation;
    use crate::preference::Preference;
    use crate::squad::Squad;
    use crate::syndromes::Curse;
    use crate::syndromes::CurseType;
    use crate::syndromes::Syndrome;
    use crate::time::DfTime;
    use crate::caste::caste::Caste;
    use crate::data::gamedata::*;
    use crate::data::memorylayout::*;
    use crate::histfigure::HistoricalFigure;
    use crate::race::race::Race;
    use crate::win::memory::memory::enum_mem_vec;
    use crate::win::memory::memory::read_mem;
    use crate::win::memory::memory::read_raw;
    use crate::win::process::Process;
    use crate::{util::memory::read_mem_as_string, DFInstance};

    #[derive(Default, Serialize, Deserialize, Clone, Debug)]
    pub struct Dwarf {
        pub addr: usize,
        pub id: i32,
        pub civ_id: i32,
        pub raw_prof_id: u8,
        pub histfig_id: i32,
        pub histfig: HistoricalFigure,
        pub turn_count: i32,
        pub states: HashMap<i16, i32>,

        pub race: Race,
        pub caste: Caste,
        pub souls: Vec<usize>,
        pub birth_date: DfTime,
        pub real_birth_date: DfTime,
        pub _age: DfTime,
        pub age: u64,
        pub arrival_time: DfTime,
        pub body_size: i32,
        pub body_size_base: i32,
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

        pub personality_addr: usize,
        pub beliefs: Vec<(Beliefs, i16)>,
        pub traits: Vec<(Facet, i16)>,
        pub goals: Vec<(Goal, i16)>,
        pub goals_realized: i32,
        pub thought_ids: Vec<i32>,
        pub thoughts: Vec<Thought>,
        pub stress_level: i32,
        pub happiness_level: HappinessLevel,
        pub mood: Mood,
        pub locked_mood: bool,
        pub syndromes: Vec<Syndrome>,
        pub is_cursed: bool,
        pub curse: Curse,

        pub squad: Squad,
        pub squad_position: i32,
        pub pending_squad_id: i32,
        pub pending_squad_position: i32,
        pub pending_squad_name: String,

        pub noble_position: FortressPosition,
        pub labors: HashMap<i32, bool>,
    }

    impl Dwarf {
        pub unsafe fn new(df: &DFInstance, proc: &Process, addr: usize) -> Result<Dwarf, Error> {
            let mut d = Dwarf{
                addr,
                id:     read_mem::<i32>(&proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "id")),
                civ_id: read_mem::<i32>(&proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "civ")),
                ..Default::default()
            };

            // check if the creature is from the same civ as the fort
            if d.civ_id != df.dwarf_civ_id {
                return Err(Error);
            }

            // read race/caste before anything else to filter out non-dwarves
            d.read_race_and_caste(df, proc)?;
            d.read_names(df, proc);
            d.read_states(df, proc);
            d.read_profession(df, proc);
            d.read_age(df, proc);
            d.read_historical_figure(df, proc);
            d.read_fake_identity();
            d.read_squad(df, proc);
            // TODO: current job
            d.read_labors(df, proc);
            // TODO: uniform
            d.read_body_size(df, proc);
            d.read_syndromes(df, proc);
            d.read_soul(df, proc);
            d.read_traits(df, proc);
            d.read_mood(df, proc);
            d.read_emotions(df, proc);
            d.read_beliefs(df, proc);
            d.read_goals(df, proc);
            d.read_gender_orientation(df, proc);
            d.read_noble_position(df);
            d.read_preferences(df, proc);
            Ok(d)
        }

        unsafe fn read_body_size(&mut self, df: &DFInstance, proc: &Process) {
            self.body_size      = read_mem::<i32>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "size_info"));
            self.body_size_base = read_mem::<i32>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "size_base"));
        }

        pub unsafe fn read_labors(&mut self, df: &DFInstance, proc: &Process) {
            let addr = self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "labors");
            let mut buf = vec![0u8; 94];
            read_raw(&proc.handle, addr, buf.len(), buf.as_mut_ptr());

            self.labors = df.game_data.labors.iter().map(|labor| (labor.id, buf[labor.id as usize] > 0)).collect();
        }

        unsafe fn read_syndromes(&mut self, df: &DFInstance, proc: &Process) {
            let syndromes_addr = self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "active_syndrome_vector");
            let syndromes = enum_mem_vec(&proc.handle, syndromes_addr);

            for s in syndromes {
                let syn = Syndrome::new(df, proc, s);

                let d = syn.clone().display_name().to_lowercase();
                match d {
                    d if d.contains("vampcurse") => {
                        self.is_cursed = true;
                        self.curse = Curse{
                            name: "Vampirism".to_string(),
                            curse_type: CurseType::Vampire,}
                    },
                    d if d.contains("werecurse") => {
                        self.is_cursed = true;
                        self.curse = Curse{
                            name: "Werebeast".to_string(),
                            curse_type: CurseType::Werebeast,}
                    },
                    d if d.contains("curse") => {
                        self.is_cursed = true;
                        self.curse = Curse{
                            name: "Curse".to_string(),
                            curse_type: CurseType::Other,}
                    },
                    _ => (),
                }

                if syn.has_transform == true {
                    let race_id = syn.transform_race;
                    if race_id >= 0 {
                        let trans_race = df.races.iter().find(|&x| x.id == race_id).unwrap();
                        // TODO: crazed night creature
                    }
                }

                self.syndromes.push(syn);
                // TODO: attribute changes
            }
        }

        unsafe fn read_squad(&mut self, df: &DFInstance, proc: &Process) {
            let squad_id: i32   = read_mem::<i32>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "squad_id"));
            self.squad_position = read_mem::<i32>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "squad_position"));
            self.pending_squad_position = self.squad_position;

            if squad_id >= 0 {// && animal, adult
                let s = df.squads.iter().find(|&x| x.id == squad_id).unwrap();
                if s.id != 0 {
                    self.squad = s.clone();
                }
            }
        }

        unsafe fn read_age(&mut self, df: &DFInstance, proc: &Process) {
            let mut birth_year = read_mem::<i32>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "birth_year"));
            let mut birth_time = read_mem::<i32>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "birth_time"));
            self.age = (df.current_time(proc).to_years() as i32).abs_diff(birth_year) as u64;

            // dwarfs can be older than time itself, but unsigned integers cannot
            if birth_year < 0 || birth_time < 0 {
                birth_year = 0;
                birth_time = 0;
            }
            self.birth_date    = DfTime::from_years(birth_year as u64) + DfTime::from_seconds(birth_time as u64);
            self.turn_count    = read_mem::<i32>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "turn_count"));
            self.arrival_time  = df.current_time(proc).sub(self.turn_count as u64);

        }

        unsafe fn read_historical_figure(&mut self, df: &DFInstance, proc: &Process) {
            self.histfig_id = read_mem::<i32>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "hist_id"));
            if df.historical_figures.contains_key(&self.histfig_id) {
                self.histfig = HistoricalFigure::new(df, proc, self.histfig_id);
            }
        }

        unsafe fn read_fake_identity(&mut self) {
            if self.histfig.has_fake_identity {
                self.real_name = self.nice_name.clone();
                self.real_birth_date = self.birth_date;

                self.first_name = self.histfig.fake_identity.fake_name.clone();
                self.nickname = self.histfig.fake_identity.fake_nickname.clone();
                let fake_birth_year = DfTime::from_years(self.histfig.fake_identity.fake_birth_year as u64);
                let fake_birth_time = DfTime::from_seconds(self.histfig.fake_identity.fake_birth_time as u64);
                self.birth_date = fake_birth_year + fake_birth_time;
                // TODO: last name
            }
        }

        pub unsafe fn read_noble_position(&mut self, df: &DFInstance) {
            self.noble_position = match df.nobles.get(&self.histfig_id) {
                Some(pos) => pos.clone(),
                None => FortressPosition::default()
            };
        }

        unsafe fn read_gender_orientation(&mut self, df: &DFInstance, proc: &Process) {
            let orientation_byte = read_mem::<u8>(&proc.handle, self.souls[0] + df.memory_layout.field_offset(OffsetSection::Soul, "orientation"));
            let male_interest = Commitment::from((orientation_byte & (3<<1))>>1);
            let female_interest = Commitment::from((orientation_byte & (3<<3))>>3);

            self.sex = Sex::from(read_mem::<u8>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "sex")));
            self.orient_vec = vec![male_interest, female_interest];
            self.orientation = match (self.sex, male_interest, female_interest) {
                (Sex::Male, Commitment::Uninterested, Commitment::Uninterested) => Orientation::Asexual,
                (Sex::Male, _, Commitment::Uninterested) => Orientation::Homosexual,
                (Sex::Male, Commitment::Uninterested, _) => Orientation::Heterosexual,
                (Sex::Male, _, _) => Orientation::Bisexual,
                (Sex::Female, Commitment::Uninterested, Commitment::Uninterested) => Orientation::Asexual,
                (Sex::Female, _, Commitment::Uninterested) => Orientation::Heterosexual,
                (Sex::Female, Commitment::Uninterested, _) => Orientation::Homosexual,
                (Sex::Female, _, _) => Orientation::Bisexual,
                _ => Orientation::Asexual,
            };
        }

        unsafe fn read_soul(&mut self, df: &DFInstance, proc: &Process) {
            self.souls = enum_mem_vec(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "souls"));
            if self.souls.len() > 1 {
                println!("Dwarf has more than one soul");
            }
            // get personality from the first soul
            self.personality_addr = self.souls[0] + df.memory_layout.field_offset(OffsetSection::Soul, "personality");
        }

        unsafe fn read_race_and_caste(&mut self, df: &DFInstance, proc: &Process) -> Result<(), Error> {
            let race_id = read_mem::<i32>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "race"));
            let race = df.get_race(race_id).unwrap();
            if race.name != "dwarf" {
                return Err(Error);
            }

            // I'm pretty sure this doesn't work as intended but dwarves only have 2 castes so it doesn't matter for now
            let caste_id = read_mem::<i32>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "caste"));
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

        unsafe fn read_states(&mut self, df: &DFInstance, proc: &Process) {
            self.states = enum_mem_vec(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "states"))
                .iter()
                .map(|&s| {
                    let k = read_mem::<i16>(&proc.handle, s);
                    let v = read_mem::<i32>(&proc.handle, s + 0x4); // 0x4 or sizeof usize?
                    (k, v)
                })
                .collect();
        }

        pub unsafe fn read_names(&mut self, df: &DFInstance, proc: &Process) {
            let name_offset =  self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "name");
            self.first_name = read_mem_as_string(&proc, name_offset + df.memory_layout.field_offset(OffsetSection::Word, "first_name"));
            self.nickname = read_mem_as_string(&proc, name_offset + df.memory_layout.field_offset(OffsetSection::Word, "nickname"));
            // TODO: last_name
            self.last_name = "".to_string();
        }

        pub unsafe fn read_last_name(df: &DFInstance, proc: &Process, offset: usize) -> String {
            df.languages.language_word(df, proc, offset)
        }

        pub unsafe fn read_profession(&mut self, df: &DFInstance, proc: &Process) {
            self.raw_prof_id = read_mem::<u8>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "profession"));
            let prof = df.game_data.professions.iter().find(|&x| x.id == self.raw_prof_id as i32).unwrap();
            self.profession = prof.clone();
            // TODO: custom profession
        }

        pub unsafe fn read_beliefs(&mut self, df: &DFInstance, proc: &Process) {
            self.beliefs = enum_mem_vec(&proc.handle, self.personality_addr + df.memory_layout.field_offset(OffsetSection::Soul, "beliefs"))
                .iter()
                .filter_map(|&addr| {
                    let belief_id = read_mem::<i32>(&proc.handle, addr);
                    if belief_id >= 0 {
                        let b = df.game_data.beliefs[belief_id as usize].clone();
                        let val = read_mem::<i16>(&proc.handle, addr + 0x4);
                        Some((b, val))
                    } else {
                        None
                    }
                })
                .collect();
        }

        pub unsafe fn read_traits(&mut self, df: &DFInstance, proc: &Process) {
            let traits_addr = self.personality_addr + df.memory_layout.field_offset(OffsetSection::Soul, "traits");
            for (i, _) in df.game_data.facets.iter().enumerate() {
                let mut tr = df.game_data.facets[i].clone();
                let val = read_mem::<i16>(&proc.handle, traits_addr + i * 2);

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
            let combat_hardened_base = read_mem::<i16>(&proc.handle, self.personality_addr + df.memory_layout.field_offset(OffsetSection::Soul, "combat_hardened"));
            let combat_hardened = ((combat_hardened_base*(90-40)) / 100) + 40;
            let f = Facet{
                id: 0,
                name: "Combat Hardened".to_string(),
                ..Default::default()
            };
            self.traits.push((f, combat_hardened));

            // TODO: cave adapt/other special traits

        }

        pub unsafe fn read_goals(&mut self, df: &DFInstance, proc: &Process) {
            self.goals = enum_mem_vec::<usize>(&proc.handle, self.personality_addr + df.memory_layout.field_offset(OffsetSection::Soul, "goals"))
                .iter()
                .filter_map(|&addr| {
                    let goal_type = read_mem::<i32>(&proc.handle, addr + 0x4);
                    if goal_type >= 0 {
                        let goal = df.game_data.goals.iter().find(|&x| x.id == goal_type).unwrap().clone();
                        let val = read_mem::<i16>(&proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Soul, "goal_realized"));
                        if val > 0 { self.goals_realized += 1; }
                        Some((goal, val))
                    } else {
                        None
                    }
                })
                .collect();
        }

        pub unsafe fn read_preferences(&mut self, df: &DFInstance, proc: &Process) {
            let prefs: Vec<usize> = enum_mem_vec(&proc.handle,  self.souls[0] + df.memory_layout.field_offset(OffsetSection::Soul, "preferences"));
            for p in prefs {
                let pref = Preference::new(df, proc, p);
                // TODO: add to preferences
            }

        }

        pub unsafe fn read_emotions(&mut self, df: &DFInstance, proc: &Process) {
            let thoughts = enum_mem_vec::<usize>(&proc.handle, self.personality_addr + df.memory_layout.field_offset(OffsetSection::Soul, "emotions"));
            // ensure traits are loaded first

            for th in thoughts {
                let thought = Thought::new(df, proc, self, th);

                // TODO: sort in descending order
                if thought.id >= 0 {
                    self.thought_ids.push(thought.id);
                }

                self.thoughts.push(thought);
            }
            // TODO: dated emotions
            self.read_happiness_level(df, proc);
            //TODO: Fix trauma
            // self.check_trauma(); // lol I know that feel
        }

        pub unsafe fn read_happiness_level(&mut self, df: &DFInstance, proc: &Process) {
            let stress_level_addr = self.personality_addr + df.memory_layout.field_offset(OffsetSection::Soul, "stress_level");
            self.stress_level = read_mem::<i32>(&proc.handle, stress_level_addr);
            let mut happiness_level = df.game_data.happiness_levels[0].clone();
            for h in &df.game_data.happiness_levels {
                if (self.stress_level - h.threshold).abs() < (self.stress_level - happiness_level.threshold).abs() {
                    happiness_level = h.clone();
                }
            }
            self.happiness_level = happiness_level;
        }

        // pub unsafe fn check_trauma(&mut self) {
        //     if self.mood == Mood::Trauma {
        //         let stress_msg = "has been overthrown by the stresses of day-to-day living";
        //         self.emotions.insert(0, UnitEmotion{
        //             emotion: stress_msg.to_string(),
        //             color: 0,
        //             divider: 0,
        //         });
        //     }
        // }

        pub unsafe fn read_mood(&mut self, df: &DFInstance, proc: &Process) {
            let mood_id = read_mem::<i16>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "mood"));
            let mut mood = Mood::from(mood_id);

            if mood == Mood::None {
                let temp_mood = read_mem::<i16>(&proc.handle, self.addr + df.memory_layout.field_offset(OffsetSection::Dwarf, "temp_mood"));
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

    pub fn print_dwarf(d: &Dwarf) {
        println!("----------------------------");
        println!(
            "{}", format!(
            "Name: {}, Profession: {}\n\
            Position: {}\n\
            Age: {} | {:?}\n\
            Sex: {:?}\n\
            Orientation: {:?}\n\
            Mood: {:?}\n\
            Stress Level: {}\n\
            Happiness Level: {:?}\n",
            d.first_name, d.profession.name, d.noble_position.name,
            d.age, d.birth_date,
            d.sex, d.orientation, d.mood,
            d.stress_level, d.happiness_level
        ));

        println!("----------------------------");
        println!("Thoughts");
        println!("----------------------------");
        for e in d.thoughts.iter() {
            println!("{:?}", e);
        }

        println!("----------------------------");
        println!("Traits");
        println!("----------------------------");
        for t in d.traits.iter() {
            println!("{} | Value: {}", t.0.name, t.1);
        }

        println!("\n----------------------------");
        println!("Beliefs");
        println!("----------------------------");
        for b in d.beliefs.iter() {
            println!("{:?} | Value: {}", b.0.name, b.1);
        }

        println!("\n----------------------------");
        println!("Goals");
        println!("----------------------------");
        for g in d.goals.iter() {
            println!("{:?} | Value: {}", g.0.name, g.1);
        }
        println!("----------------------------");
        println!("\n");

    }

    #[derive(Default, Debug, PartialEq, Clone, Serialize, Deserialize)]
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

    #[derive(Default, Debug, PartialEq, Serialize, Deserialize, Clone, Copy)]
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

}