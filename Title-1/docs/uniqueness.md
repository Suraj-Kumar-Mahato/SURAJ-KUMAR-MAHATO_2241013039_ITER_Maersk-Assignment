# Uniqueness & Explainability

1) **Offline-first queue**: Android holds data when network is unavailable; files flushed when connectivity returns.
2) **Privacy by design**: Device identifiers are hashed (salted SHA-256) before leaving device.
3) **Pluggable metric adapters**: Clear abstraction to later add vendor APIs (QXDM, chipset SDKs).
4) **One-command backend**: Docker Compose spins up API + dashboard.
5) **Map-ready GeoJSON**: Interoperable format for GIS analysis.
6) **Minimal dependencies**: SQLite for easy assessment, can switch to Postgres.
7) **Clean code**: Clear separation of concerns with comments and simple data models.
