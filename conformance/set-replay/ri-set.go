// This program runs the RI Set implementations with canonical Set syntax and supplied Items.
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"

	"github.com/vanderpol/scap-ng-ri/evaluate"
	"github.com/vanderpol/scap-ng-ri/runtimecore"
)

type operand struct {
	Object  string            `json:"object"`
	Set     *expression       `json:"set"`
	Filters []json.RawMessage `json:"filters"`
}

type expression struct {
	Operator string    `json:"operator"`
	Operands []operand `json:"operands"`
}

type population struct {
	Complete bool              `json:"complete"`
	Items    []json.RawMessage `json:"items"`
}

type replayCase struct {
	Expression  expression            `json:"expression"`
	Populations map[string]population `json:"populations"`
	Cancelled   bool                  `json:"cancelled"`
}

type observation struct {
	IDs        []string `json:"ids"`
	Complete   bool     `json:"complete"`
	Diagnostic string   `json:"diagnostic,omitempty"`
}

type cursor struct {
	index int
	data  evaluate.SetOperand
}

func (c *cursor) Next(ctx context.Context) (evaluate.SetItem, error) {
	if err := ctx.Err(); err != nil {
		return evaluate.SetItem{}, err
	}
	if c.index == len(c.data.Items) {
		return evaluate.SetItem{}, io.EOF
	}
	item := c.data.Items[c.index]
	c.index++
	return item, nil
}

func (*cursor) Close() error     { return nil }
func (c *cursor) Complete() bool { return c.data.Complete }

type sink struct{ items []evaluate.SetItem }

func (s *sink) Append(_ context.Context, item evaluate.SetItem) error {
	s.items = append(s.items, item)
	return nil
}

type resolver func(context.Context, string, []evaluate.SetOperand, [][]evaluate.SetFilter) (evaluate.SetResult, error)

func stream(ctx context.Context, op string, inputs []evaluate.SetOperand, filters [][]evaluate.SetFilter) (evaluate.SetResult, error) {
	cursors := make([]evaluate.SetCursor, 0, len(inputs))
	for _, input := range inputs {
		cursors = append(cursors, &cursor{data: input})
	}
	output := &sink{}
	result, err := runtimecore.ResolveSetStreaming(ctx, op, cursors, filters, output)
	return evaluate.SetResult{Items: output.items, Complete: result.Complete}, err
}

func resolve(ctx context.Context, expr expression, populations map[string]population, run resolver) (evaluate.SetResult, error) {
	inputs := make([]evaluate.SetOperand, 0, len(expr.Operands))
	filters := make([][]evaluate.SetFilter, 0, len(expr.Operands))
	for _, part := range expr.Operands {
		var input evaluate.SetOperand
		if part.Set != nil {
			subset, err := resolve(ctx, *part.Set, populations, run)
			if err != nil {
				return evaluate.SetResult{}, err
			}
			input = evaluate.SetOperand{Items: subset.Items, Complete: subset.Complete}
		} else {
			data, ok := populations[part.Object]
			if !ok {
				return evaluate.SetResult{}, fmt.Errorf("missing population %s", part.Object)
			}
			input.Complete = data.Complete
			for _, raw := range data.Items {
				var value struct {
					ID string `json:"id"`
				}
				if err := json.Unmarshal(raw, &value); err != nil {
					return evaluate.SetResult{}, err
				}
				input.Items = append(input.Items, evaluate.SetItem{ID: value.ID, Payload: raw})
			}
		}
		compiled, diagnostic := evaluate.CompileSetFilters(part.Filters, "/set/filters")
		if diagnostic != nil {
			return evaluate.SetResult{}, diagnostic
		}
		inputs = append(inputs, input)
		filters = append(filters, compiled)
	}
	return run(ctx, expr.Operator, inputs, filters)
}

func record(ctx context.Context, entry replayCase, run resolver) observation {
	result, err := resolve(ctx, entry.Expression, entry.Populations, run)
	row := observation{IDs: make([]string, 0, len(result.Items)), Complete: result.Complete}
	if err != nil {
		row.Diagnostic = err.Error()
	}
	for _, item := range result.Items {
		row.IDs = append(row.IDs, item.ID)
	}
	return row
}

func main() {
	var input map[string]replayCase
	if err := json.NewDecoder(os.Stdin).Decode(&input); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	output := make(map[string]map[string]observation, len(input))
	for name, entry := range input {
		ctx, cancel := context.WithCancel(context.Background())
		if entry.Cancelled {
			cancel()
		}
		output[name] = map[string]observation{
			"memory": record(ctx, entry, evaluate.ResolveSet),
			"stream": record(ctx, entry, stream),
		}
		cancel()
	}
	if err := json.NewEncoder(os.Stdout).Encode(output); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
