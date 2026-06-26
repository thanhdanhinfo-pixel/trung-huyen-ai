Drive Reader Capability Registry

Status: PRODUCTION

Supported Capabilities

listDriveFiles

Endpoint:

GET /drive/files

Status: STABLE

---

searchDrive

Endpoint:

GET /drive/search?q=...

Status: STABLE

---

readDriveFile

Endpoint:

GET /drive/read?file_id=...

Status: STABLE

---

listDriveDirectory

Endpoint:

GET /drive/list-path?path=...

Status: STABLE

---

readDrivePath

Endpoint:

GET /drive/read-path?path=...

Status: EXPERIMENTAL

Reason:

- Multi-root ambiguity
- Recursive traversal cost O(N)
- Potential Cloud Run timeout

Recommendation:

Prefer:

GET /drive/read?file_id=...

for production workloads.
