use serde::{Deserialize, Serialize};

use crate::{data::{gamedata::{Subthought, UnitThoughts}, memorylayout::OffsetSection}, dfinstance::DFInstance, dwarf::dwarf::Dwarf, time::DfTime, win::{memory::memory::read_mem, process::Process}};

#[derive(Default, Serialize, Deserialize, Clone, Debug)]
pub struct Thought {
    pub id: i32,
    pub emotion_type: EmotionType,
    pub data: UnitThoughts,
    pub thought: String,
    pub subthought: Subthought,
    pub subthought_id: i32,
    pub placeholder: String,

    pub count: i32,
    pub strength: i32,
    // TODO: implement effects
    pub effect: f32,
    pub divider: i32,
    pub multiplier: f32,
    pub optional_levels: i32,
    pub compare_id: String,
    pub time: DfTime,
}

impl Thought {
    pub unsafe fn new(df: &DFInstance, proc: &Process, dwarf: &Dwarf, addr: usize) -> Self {
        let mut t = Thought{
            id:              read_mem::<i32>(&proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Emotion, "thought_id")),
            emotion_type:    EmotionType::from(read_mem::<i32>(&proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Emotion, "emotion_type"))),
            strength:        read_mem::<i32>(&proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Emotion, "strength")),
            subthought_id:   read_mem::<i32>(&proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Emotion, "sub_id")),
            optional_levels: read_mem::<i32>(&proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Emotion, "level")),
            ..Default::default()
        };

        let year      = DfTime::from_years(read_mem::<i32>(&proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Emotion, "year")) as u64);
        let year_tick = DfTime::from_seconds(read_mem::<i32>(&proc.handle, addr + df.memory_layout.field_offset(OffsetSection::Emotion, "year_tick")) as u64);
        t.time        = year + year_tick;

        match df.game_data.unit_thoughts.get(t.id as usize - 1) {
            Some(data) => {
                t.data = data.clone();
                t.thought = t.data.thought.clone();
                t.check_subthought(df);
                t.calculate_effect(df, dwarf);
            },
            None => {
                eprintln!("Warning: Thought with id {} not found", t.id);
                t.data = UnitThoughts::default();
            }
        }

        t
    }

    fn check_subthought(&mut self, df: &DFInstance) {
        // TODO: I might be able to simplify this after I fix the subthoughts data

        // seemingly, subthoughts_type 0 and 1 are weird
        if self.data.subthoughts_type < 2 {
            return;
        }

        match df.game_data.unit_subthoughts.get(self.data.subthoughts_type as usize) {
            Some(data) => {
                self.placeholder = data.placeholder.clone();
                self.subthought = match data.subthoughts.iter().find(|s| s.id == self.subthought_id) {
                    Some(subthought) => subthought.clone(),
                    None => {
                        eprintln!("Warning: Subthought with id {} not found", self.subthought_id);
                        Subthought::default()
                    }
                };

                if self.placeholder == "" {
                    // if the placeholder is empty, append the subthought to the thought
                    self.thought = self.thought.clone() + &self.subthought.thought.clone();
                } else {
                    // otherwise, replace the placeholder with the subthought
                    self.thought = self.thought.replace(self.placeholder.as_str(), self.subthought.thought.as_str());
                }
            },
            None => {
                eprintln!("Warning: Subthoughts with id {} not found", self.data.subthoughts_type);
                return;
            }
        };
    }

    fn calculate_effect(&mut self, df: &DFInstance, dwarf: &Dwarf) {
        let mut base_effect = 1.0;
        let stress_vuln: i16 = dwarf.traits.get(8).unwrap().2;

        self.divider = df.game_data.unit_emotions.get(self.emotion_type as usize).unwrap().divider;
        self.multiplier = match stress_vuln {
            s if s >= 91 => 5.0,
            s if s >= 76 => 3.0,
            s if s >= 61 => 2.0,
            s if s <= 24 => 0.25,
            s if s <= 39 => 0.5,
            s if s <= 9 => {
                self.divider = 0;
                0.0
            },
            _ => {
                self.divider = 0;
                0.0
            },
        };

        if self.divider != 0 {
            base_effect = (self.strength / self.divider) as f32;
        }

        self.effect = base_effect * self.multiplier;
    }
}

#[derive(Default, Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum EmotionType {
    #[default]
    None = -1,
    Acceptance,
    Adoration,
    Affection,
    Agitation,
    Aggravation,
    Agony,
    Alarm,
    Alienation,
    Amazement,
    Ambivalence,
    Amusement,
    Anger,
    ExistentialCrisis,
    Anguish,
    Annoyance,
    Unknown15,
    Anxiety,
    Apathy,
    Unknown18,
    Arousal,
    Astonishment,
    Unknown21,
    Aversion,
    Awe,
    Bitterness,
    Bliss,
    Boredom,
    Caring,
    Unknown28,
    Confusion,
    Contempt,
    Contentment,
    Unknown32,
    Unknown33,
    Defeated,
    Dejection,
    Delight,
    Unknown37,
    Unknown38,
    Despair,
    Disappointment,
    Disgust,
    Disillusioned,
    Dislike,
    Dismay,
    Displeasure,
    Distress,
    Doubt,
    Unknown48,
    Eagerness,
    Unknown50,
    Elation,
    Embarrassment,
    Empathy,
    Emptiness,
    Enjoyment,
    Unknown56,
    Enthusiastic,
    Unknown58,
    Euphoric,
    Exasperation,
    Excited,
    Exhilaration,
    Expectant,
    Fear,
    Ferocity,
    Fondness,
    Free,
    Fright,
    Frustration,
    Unknown70,
    Unknown71,
    Unknown72,
    Glee,
    Gloom,
    Glumness,
    Gratitude,
    Unknown77,
    Grief,
    GrimSatisfaction,
    Grouchiness,
    Grumpiness,
    Guilt,
    Happiness,
    Hatred,
    Unknown85,
    Hope,
    Hopelessness,
    Horror,
    Unknown89,
    Humiliation,
    Unknown91,
    Unknown92,
    Unknown93,
    Unknown94,
    Insult,
    Interest,
    Irritation,
    Isolation,
    Unknown99,
    Jolliness,
    Jovialty,
    Joy,
    Jubilation,
    Unknown104,
    Loathing,
    Loneliness,
    Unknown107,
    Love,
    Unknown109,
    Lust,
    Unknown111,
    Misery,
    Mortification,
    Unknown114,
    Nervousness,
    Nostalgia,
    Optimism,
    Outrage,
    Panic,
    Patience,
    Passion,
    Pessimistic,
    Unknown123,
    Pleasure,
    Pride,
    Rage,
    Rapture,
    Rejection,
    Relief,
    Regret,
    Remorse,
    Repentance,
    Resentment,
    Unknown134,
    RighteousIndignation,
    Sadness,
    Satisfaction,
    Unknown138,
    SelfPity,
    Unknown140,
    Servile,
    Shaken,
    Shame,
    Shock,
    Unknown145,
    Unknown146,
    Unknown147,
    Unknown148,
    Suspicion,
    Sympathy,
    Tenderness,
    Unknown152,
    Terror,
    Thrill,
    Unknown155,
    Triumph,
    Uneasiness,
    Unhappiness,
    Vengefulness,
    Unknown160,
    Wonder,
    Worry,
    Wrath,
    Zeal,
    Unknown165,
    Unknown166,
    Unknown167,
    Restless,
    Admiration,
}

impl From<i32> for EmotionType {
    fn from(value: i32) -> Self {
        match value {
            -1 => EmotionType::None,
            0 => EmotionType::Acceptance,
            1 => EmotionType::Adoration,
            2 => EmotionType::Affection,
            3 => EmotionType::Agitation,
            4 => EmotionType::Aggravation,
            5 => EmotionType::Agony,
            6 => EmotionType::Alarm,
            7 => EmotionType::Alienation,
            8 => EmotionType::Amazement,
            9 => EmotionType::Ambivalence,
            10 => EmotionType::Amusement,
            11 => EmotionType::Anger,
            12 => EmotionType::ExistentialCrisis,
            13 => EmotionType::Anguish,
            14 => EmotionType::Annoyance,
            15 => EmotionType::Unknown15,
            16 => EmotionType::Anxiety,
            17 => EmotionType::Apathy,
            18 => EmotionType::Unknown18,
            19 => EmotionType::Arousal,
            20 => EmotionType::Astonishment,
            21 => EmotionType::Unknown21,
            22 => EmotionType::Aversion,
            23 => EmotionType::Awe,
            24 => EmotionType::Bitterness,
            25 => EmotionType::Bliss,
            26 => EmotionType::Boredom,
            27 => EmotionType::Caring,
            28 => EmotionType::Unknown28,
            29 => EmotionType::Confusion,
            30 => EmotionType::Contempt,
            31 => EmotionType::Contentment,
            32 => EmotionType::Unknown32,
            33 => EmotionType::Unknown33,
            34 => EmotionType::Defeated,
            35 => EmotionType::Dejection,
            36 => EmotionType::Delight,
            37 => EmotionType::Unknown37,
            38 => EmotionType::Unknown38,
            39 => EmotionType::Despair,
            40 => EmotionType::Disappointment,
            41 => EmotionType::Disgust,
            42 => EmotionType::Disillusioned,
            43 => EmotionType::Dislike,
            44 => EmotionType::Dismay,
            45 => EmotionType::Displeasure,
            46 => EmotionType::Distress,
            47 => EmotionType::Doubt,
            48 => EmotionType::Unknown48,
            49 => EmotionType::Eagerness,
            50 => EmotionType::Unknown50,
            51 => EmotionType::Elation,
            52 => EmotionType::Embarrassment,
            53 => EmotionType::Empathy,
            54 => EmotionType::Emptiness,
            55 => EmotionType::Enjoyment,
            56 => EmotionType::Unknown56,
            57 => EmotionType::Enthusiastic,
            58 => EmotionType::Unknown58,
            59 => EmotionType::Euphoric,
            60 => EmotionType::Exasperation,
            61 => EmotionType::Excited,
            62 => EmotionType::Exhilaration,
            63 => EmotionType::Expectant,
            64 => EmotionType::Fear,
            65 => EmotionType::Ferocity,
            66 => EmotionType::Fondness,
            67 => EmotionType::Free,
            68 => EmotionType::Fright,
            69 => EmotionType::Frustration,
            70 => EmotionType::Unknown70,
            71 => EmotionType::Unknown71,
            72 => EmotionType::Unknown72,
            73 => EmotionType::Glee,
            74 => EmotionType::Gloom,
            75 => EmotionType::Glumness,
            76 => EmotionType::Gratitude,
            77 => EmotionType::Unknown77,
            78 => EmotionType::Grief,
            79 => EmotionType::GrimSatisfaction,
            80 => EmotionType::Grouchiness,
            81 => EmotionType::Grumpiness,
            82 => EmotionType::Guilt,
            83 => EmotionType::Happiness,
            84 => EmotionType::Hatred,
            85 => EmotionType::Unknown85,
            86 => EmotionType::Hope,
            87 => EmotionType::Hopelessness,
            88 => EmotionType::Horror,
            89 => EmotionType::Unknown89,
            90 => EmotionType::Humiliation,
            91 => EmotionType::Unknown91,
            92 => EmotionType::Unknown92,
            93 => EmotionType::Unknown93,
            94 => EmotionType::Unknown94,
            95 => EmotionType::Insult,
            96 => EmotionType::Interest,
            97 => EmotionType::Irritation,
            98 => EmotionType::Isolation,
            99 => EmotionType::Unknown99,
            100 => EmotionType::Jolliness,
            101 => EmotionType::Jovialty,
            102 => EmotionType::Joy,
            103 => EmotionType::Jubilation,
            104 => EmotionType::Unknown104,
            105 => EmotionType::Loathing,
            106 => EmotionType::Loneliness,
            107 => EmotionType::Unknown107,
            108 => EmotionType::Love,
            109 => EmotionType::Unknown109,
            110 => EmotionType::Lust,
            111 => EmotionType::Unknown111,
            112 => EmotionType::Misery,
            113 => EmotionType::Mortification,
            114 => EmotionType::Unknown114,
            115 => EmotionType::Nervousness,
            116 => EmotionType::Nostalgia,
            117 => EmotionType::Optimism,
            118 => EmotionType::Outrage,
            119 => EmotionType::Panic,
            120 => EmotionType::Patience,
            121 => EmotionType::Passion,
            122 => EmotionType::Pessimistic,
            123 => EmotionType::Unknown123,
            124 => EmotionType::Pleasure,
            125 => EmotionType::Pride,
            126 => EmotionType::Rage,
            127 => EmotionType::Rapture,
            128 => EmotionType::Rejection,
            129 => EmotionType::Relief,
            130 => EmotionType::Regret,
            131 => EmotionType::Remorse,
            132 => EmotionType::Repentance,
            133 => EmotionType::Resentment,
            134 => EmotionType::Unknown134,
            135 => EmotionType::RighteousIndignation,
            136 => EmotionType::Sadness,
            137 => EmotionType::Satisfaction,
            138 => EmotionType::Unknown138,
            139 => EmotionType::SelfPity,
            140 => EmotionType::Unknown140,
            141 => EmotionType::Servile,
            142 => EmotionType::Shaken,
            143 => EmotionType::Shame,
            144 => EmotionType::Shock,
            145 => EmotionType::Unknown145,
            146 => EmotionType::Unknown146,
            147 => EmotionType::Unknown147,
            148 => EmotionType::Unknown148,
            149 => EmotionType::Suspicion,
            150 => EmotionType::Sympathy,
            151 => EmotionType::Tenderness,
            152 => EmotionType::Unknown152,
            153 => EmotionType::Terror,
            154 => EmotionType::Thrill,
            155 => EmotionType::Unknown155,
            156 => EmotionType::Triumph,
            157 => EmotionType::Uneasiness,
            158 => EmotionType::Unhappiness,
            159 => EmotionType::Vengefulness,
            160 => EmotionType::Unknown160,
            161 => EmotionType::Wonder,
            162 => EmotionType::Worry,
            163 => EmotionType::Wrath,
            164 => EmotionType::Zeal,
            165 => EmotionType::Unknown165,
            166 => EmotionType::Unknown166,
            167 => EmotionType::Unknown167,
            168 => EmotionType::Restless,
            169 => EmotionType::Admiration,
            _ => EmotionType::None, // Default case for unknown values
        }
    }
}