# Native UNIX file metadata

The [Assessment](file-metadata.assessment.yaml) uses one shared file Object.
It compares the 24 canonical native field names in the
[UNIX file mapping](../../schema/capability-mappings/supported/unix.file.json).
This exercises each datatype and preserves native field names such as
`owner_uid`, `modify_time` and `owner_read`.

The [supplied snapshot](snapshot.yaml) provides a path, POSIX mode, and fixed
metadata. The [expected manifest](expected.json) records the decoded fields
and 12 mode changes. The local oracle derives each permission bit with its
POSIX mask and checks that toggling only that bit changes only its comparison.
The fixture exercises supplied evidence and metadata identity. It does not
depend on filesystem mounts, privileges, collection, or scanner output.
