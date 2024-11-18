use std::{ops::Add, time::Duration};

use serde::{Deserialize, Serialize};

pub const DF_SEASONS: [&str; 4] = ["Spring", "Summer", "Autumn", "Winter"];
pub const DF_MONTHS: [&str; 12] = [
    "Granite", "Slate", "Felsite",
    "Hematite", "Malachite", "Galena",
    "Limestone", "Sandstone", "Timber",
    "Moonstone", "Opal", "Obsidian"
];

/// a wrapper for `std::time::Duration`
#[derive(Debug, Default, Clone, Copy, Serialize, Deserialize)]
pub struct DfTime(Duration);

impl DfTime {

    pub fn current_month(&self) -> String {
        let total_days = self.to_days();
        let month_index = (total_days / 28 % 12) as usize;
        DF_MONTHS[month_index].to_string()
    }

    pub fn from_years(years: u64) -> Self {
        let year: u64 = years.checked_mul(1200 * 28 * 12).unwrap_or_default();
        DfTime(Duration::from_secs(year))
    }

    pub fn from_months(months: u64) -> Self {
        DfTime(Duration::from_secs(months * 1200 * 28))
    }

    pub fn from_weeks(weeks: u64) -> Self {
        DfTime(Duration::from_secs(weeks * 1200 * 7))
    }

    pub fn from_days(days: u64) -> Self {
        DfTime(Duration::from_secs(days * 1200))
    }

    pub fn from_hours(hours: u64) -> Self {
        DfTime(Duration::from_secs(hours * 50))
    }

    pub fn from_minutes(minutes: u64) -> Self {
        DfTime(Duration::from_secs(minutes / 12))
    }

    pub fn from_seconds(seconds: u64) -> Self {
        DfTime(Duration::from_secs(seconds))
    }

    pub fn to_years(&self) -> u64 {
        self.0.as_secs() / (1200 * 28 * 12)
    }

    pub fn to_months(&self) -> u64 {
        self.0.as_secs() / (1200 * 28)
    }

    pub fn to_weeks(&self) -> u64 {
        self.0.as_secs() / (1200 * 7)
    }

    pub fn to_days(&self) -> u64 {
        self.0.as_secs() / 1200
    }

    pub fn to_hours(&self) -> u64 {
        self.0.as_secs() / 50
    }

    pub fn to_minutes(&self) -> u64 {
        self.0.as_secs() * 12
    }

    pub fn to_seconds(&self) -> u64 {
        self.0.as_secs()
    }

    pub fn as_duration(&self) -> Duration {
        self.0
    }

    pub fn sub(&self, other: u64) -> Self {
        DfTime(self.0 - Duration::from_secs(other))
    }

}

impl Add for DfTime {
    type Output = Self;

    fn add(self, other: Self) -> Self {
        DfTime(self.0 + other.0)
    }
}