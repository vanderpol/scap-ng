# Go 1.27.3; no default /usr/bin/go substitution. All commands exit 0 unless labeled below.
export GOTOOLCHAIN=local GOPROXY=off GOPATH=/tmp/ri-pre-handoff-gopath GOCACHE=/tmp/ri-pre-handoff-gocache GOMAXPROCS=2
export PATH=/tmp/ri-pre-handoff-go/go/bin:$PATH
# RI checkout review/handoff-integration:
go mod verify
go test -race -count=1 -v ./...
go vet ./...
for target in FuzzEvaluate FuzzEvaluateTest FuzzVariableDependencies FuzzVariablePopulations FuzzEvidenceSource; do
  go test ./evaluate -run '^$' -fuzz "^${target}$" -fuzztime=10s -parallel=2
done
go build -trimpath -buildvcs=false -o /tmp/handoff-evaluate ./cmd/ri-evaluate
go build -trimpath -buildvcs=false -o /tmp/handoff-probe ./cmd/ri-evidence-probe
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build ./...
python tools/build_schema_pack.py /workspace/work/native-frozen-pre-handoff --check
python tools/check_pre_handoff_design.py --native /workspace/work/native-frozen-pre-handoff --go /tmp/ri-pre-handoff-go/go/bin/go --verify-baseline
export RI_NATIVE_SOURCE=/workspace/work/native-frozen-pre-handoff RI_OVAL_SOURCE=/tmp/ri-pre-handoff-oval-git RI_SELF_ASSERTION_SOURCE=/tmp/ri-pre-handoff-self-assertion RI_TOOLS37_SOURCE=/workspace/work/tools37 RI_EVALUATOR_BINARY=/tmp/handoff-evaluate RI_EVIDENCE_PROBE_BINARY=/tmp/handoff-probe
export RI_VARIABLE_CORPUS="$RI_SELF_ASSERTION_SOURCE" RI_VARIABLE_NATIVE="$RI_NATIVE_SOURCE" RI_VARIABLE_CANONICAL_AUDIT="$RI_NATIVE_SOURCE" RI_VARIABLE_RECORDED_AUDIT="$PWD/docs/qualification/variables/artifact-audit.json" RI_VARIABLE_OVAL_XSD="$RI_OVAL_SOURCE"
python -m unittest discover -s tests -v
python tools/check_singleton_variables.py --tools /workspace/work/tools37 --corpus /tmp/ri-pre-handoff-self-assertion --binary /tmp/handoff-evaluate --output NEW-originals.json
python tools/qualify_evidence_backends.py --binary /tmp/handoff-probe --items 100000 --output NEW-100k.json
python tools/qualify_evidence_backends.py --binary /tmp/handoff-probe --items 1000000 --output NEW-1m.json
# Canonical checkout review/handoff-integration:
python -m unittest discover -s tests -v
python tools/generate_native_selector_schema.py --check
python tools/generate_docs.py --check
python tools/generate_unix_file_reference.py --check
python tools/audit_schema_documentation.py --check
python tools/generate_approved_annotation_pilot.py --check
python tools/generate_review_documentation_pack.py --check
python tools/generate_documentation.py --check
python tools/audit_documentation_fidelity.py --check
python tools/check_documentation_examples.py --check
python tools/check_semantic_conformance.py --supplied-evidence --ri-binary /tmp/handoff-evaluate --output NEW-conformance.json
python /tmp/handoff-publication-gate/scripts/audit_publication_paths.py --root . --repository vanderpol/scap-ng --trusted-gate-commit 053eeeb3b33e3ee5f683604fd66ae8c833450cd0 --check
# Historical-eight receipt: each request is executed with /tmp/handoff-evaluate;
# exact exit code and SHA256(stdout/stderr) compared to docs/research/sqlite-performance/evidence/historical-eight.json.
# Initial integration failure, exit 1:
# python tools/generate_documentation.py --check
# reported extra docs/reference/prototypes/unix-file.md. Fixed by byte-identical relocation, not a check exemption.
# Initial packaging command, exit 2:
# git archive 053eeeb3b33e3ee5f683604fd66ae8c833450cd0 scripts publication | tar -x ...
# nonexistent publication path; corrected to scripts src docs/issue40, then checker passed.
