package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"

	"github.com/vanderpol/scap-ng-ri/evaluate"
)

type Case struct {
	Name     string                               `json:"name"`
	Test     string                               `json:"test"`
	Evidence map[string]evaluate.VariableEvidence `json:"evidence,omitempty"`
}

type Observation struct {
	Decision   evaluate.Decision    `json:"decision"`
	Diagnostic *evaluate.Diagnostic `json:"diagnostic,omitempty"`
}

func run() error {
	var input struct {
		Request     json.RawMessage            `json:"request"`
		Definitions map[string]json.RawMessage `json:"definitions"`
		Inputs      map[string]any             `json:"inputs"`
		Cases       []Case                     `json:"cases"`
	}
	decoder := json.NewDecoder(os.Stdin)
	decoder.UseNumber()
	if err := decoder.Decode(&input); err != nil {
		return err
	}
	ctx := evaluate.WithEvaluationInputs(context.Background(), input.Inputs, input.Definitions)
	results := make(map[string]Observation, len(input.Cases))
	for _, entry := range input.Cases {
		var decision evaluate.Decision
		var diagnostic *evaluate.Diagnostic
		if entry.Evidence == nil {
			decision, diagnostic = evaluate.EvaluateTest(ctx, input.Request, entry.Test)
		} else {
			decision, diagnostic = evaluate.EvaluateTestWithVariableEvidence(ctx, input.Request, entry.Test, entry.Evidence)
		}
		results[entry.Name] = Observation{Decision: decision, Diagnostic: diagnostic}
	}
	return json.NewEncoder(os.Stdout).Encode(results)
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
