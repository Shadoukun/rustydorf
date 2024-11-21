use std::fmt;

use serde::{Deserialize, Serialize};

#[derive(Default, Debug, PartialEq, Serialize, Deserialize, Clone)]
pub struct Attribute {
    pub id: i32,
    pub name: String,
    pub value: i32,
    pub value_potential: i32,
    pub value_balanced: i32,
    pub display_value: i32,
    pub max: i32,
    pub rating_potential: i32,
    pub rating: i32,
    pub cti: i32,
    pub descriptor: String,
    pub descriptor_index: i32,
}

#[derive(Debug, Default, PartialEq, Clone, Copy, Serialize, Deserialize, Eq, Hash)]
pub enum AttributeType {
    #[default]
    None = -1,
    Strength = 0,
    Agility = 1,
    Toughness = 2,
    Endurance = 3,
    Recuperation = 4,
    DiseaseResistance = 5,
    AnalyticalAbility = 6,
    Focus = 7,
    Willpower = 8,
    Creativity = 9,
    Intuition = 10,
    Patience = 11,
    Memory = 12,
    LinguisticAbility = 13,
    SpatialSense = 14,
    Musicality = 15,
    KinestheticSense = 16,
    Empathy = 17,
    SocialAwareness = 18,
}

impl From<i32> for AttributeType {
    fn from(value: i32) -> Self {
        match value {
            0 => AttributeType::Strength,
            1 => AttributeType::Agility,
            2 => AttributeType::Toughness,
            3 => AttributeType::Endurance,
            4 => AttributeType::Recuperation,
            5 => AttributeType::DiseaseResistance,
            6 => AttributeType::AnalyticalAbility,
            7 => AttributeType::Focus,
            8 => AttributeType::Willpower,
            9 => AttributeType::Creativity,
            10 => AttributeType::Intuition,
            11 => AttributeType::Patience,
            12 => AttributeType::Memory,
            13 => AttributeType::LinguisticAbility,
            14 => AttributeType::SpatialSense,
            15 => AttributeType::Musicality,
            16 => AttributeType::KinestheticSense,
            17 => AttributeType::Empathy,
            18 => AttributeType::SocialAwareness,
            _ => AttributeType::None,
        }
    }
}

impl fmt::Display for AttributeType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AttributeType::None => write!(f, "None"),
            AttributeType::Strength => write!(f, "Strength"),
            AttributeType::Agility => write!(f, "Agility"),
            AttributeType::Toughness => write!(f, "Toughness"),
            AttributeType::Endurance => write!(f, "Endurance"),
            AttributeType::Recuperation => write!(f, "Recuperation"),
            AttributeType::DiseaseResistance => write!(f, "Disease Resistance"),
            AttributeType::AnalyticalAbility => write!(f, "Analytical Ability"),
            AttributeType::Focus => write!(f, "Focus"),
            AttributeType::Willpower => write!(f, "Willpower"),
            AttributeType::Creativity => write!(f, "Creativity"),
            AttributeType::Intuition => write!(f, "Intuition"),
            AttributeType::Patience => write!(f, "Patience"),
            AttributeType::Memory => write!(f, "Memory"),
            AttributeType::LinguisticAbility => write!(f, "Linguistic Ability"),
            AttributeType::SpatialSense => write!(f, "Spatial Sense"),
            AttributeType::Musicality => write!(f, "Musicality"),
            AttributeType::KinestheticSense => write!(f, "Kinesthetic Sense"),
            AttributeType::Empathy => write!(f, "Empathy"),
            AttributeType::SocialAwareness => write!(f, "Social Awareness"),
        }
    }

}