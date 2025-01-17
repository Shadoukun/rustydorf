use log::{Record, Level, Metadata, SetLoggerError, LevelFilter};
use colored::*;

struct Logger;

static LOGGER: Logger = Logger;

impl log::Log for Logger {
    fn enabled(&self, metadata: &Metadata) -> bool {
        true
    }

    fn log(&self, record: &Record) {
        if self.enabled(record.metadata()) {
            let colored_level = match record.level() {
                Level::Error => format!("{}", record.level().to_string().red().bold()),
                Level::Warn  => format!("{}", record.level().to_string().yellow().bold()),
                Level::Info  => format!("{}", record.level().to_string().green().bold()),
                Level::Debug => format!("{}", record.level().to_string().blue().bold()),
                Level::Trace => format!("{}", record.level().to_string().white().dimmed()),
            };
            println!("{} - {}", colored_level, record.args());
        }
    }

    fn flush(&self) {
        // No need to flush since we are just printing to stdout.
    }
}

pub fn init_logger(level: LevelFilter) -> Result<(), SetLoggerError> {
    log::set_logger(&LOGGER)?;
    log::set_max_level(level);
    Ok(())
}
