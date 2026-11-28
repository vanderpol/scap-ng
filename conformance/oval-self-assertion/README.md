# Supplemental OVAL 5.12.3 Self-Assertion

The pinned upstream XML census found no `yamlfilecontent_test` or `sql512_test`.
These contributions use new OVAL IDs. See [independent expectations](expected.json)
for the typed values, decisive evidence and expected Test and Definition outcomes.

Copy the contents of `fixtures/yaml/` into the fixture directory declared for
the target platform. Use an isolated test target with a fresh fixture directory
and readable regular files. Leave `does-not-exist.yaml` absent. The file at depth
two checks the depth-one boundary. Inline cases require no filesystem.

For SQL512, load `fixtures/sqlite.sql` into a disposable SQLite database. The
source expects a collector that discovers it as instance `scap-ng-issue87`
and database `main`. SQLite itself has no service-discovery mechanism, so this
binding requires explicit collector support. The query vectors are read-only.
The SQL source contract requires trusted content for interpreter execution.

Empty YAML values, malformed YAML, nested query results, unreadable files and
parser-limit conditions still require collector-specific receipts and a reviewed
status oracle. The malformed fixture is reserved for that work. The `$.<key>`
queries and OVAL unkeyed field `#` are submitted as source cases for runtime
qualification.
