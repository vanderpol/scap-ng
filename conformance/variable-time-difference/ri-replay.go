// This program runs from the pinned RI module and uses its public evaluator.
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/vanderpol/scap-ng-ri/evaluate"
)

type replay struct {
	Test  string `json:"test"`
	Clock string `json:"clock,omitempty"`
}

func run() error {
	var input struct {
		Request json.RawMessage `json:"request"`
		Cases   []replay        `json:"cases"`
	}
	if err := json.NewDecoder(os.Stdin).Decode(&input); err != nil {
		return err
	}

	results := make([]evaluate.Decision, 0, len(input.Cases))
	for _, entry := range input.Cases {
		ctx := context.Background()
		if entry.Clock != "" {
			frozen, err := time.Parse(time.RFC3339, entry.Clock)
			if err != nil {
				return err
			}
			ctx = evaluate.WithEvaluationClock(ctx, func() time.Time { return frozen })
		}
		decision, diagnostic := evaluate.EvaluateTest(ctx, input.Request, entry.Test)
		if diagnostic != nil {
			return fmt.Errorf("%s: %w", entry.Test, diagnostic)
		}
		results = append(results, decision)
	}
	return json.NewEncoder(os.Stdout).Encode(results)
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
