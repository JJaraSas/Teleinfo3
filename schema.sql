DROP TABLE IF EXISTS sensor_data, liimte;

CREATE TABLE sensor_data (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	temperatura REAL,
	humedad REAL,
	intensidad_luz REAL,
    humedad_suelo REAL
);

CREATE TABLE limite (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	temperatura REAL,
	humedad REAL,
	intensidad_luz REAL,
    humedad_suelo REAL
);