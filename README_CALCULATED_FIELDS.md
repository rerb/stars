# Calculated Fields

All DocumentationFields have a `calculated` boolean
property. Calculated fields are those with a True value for this
property. Each calculated field has a `formula` property, which is
used to derive the value of any related DocumentationFieldSubmission
objects.

Calculated field submissions are instantiated as NumericSubmission
objects. The value of these submissions is the result of evaluating
the `formula` property of the matching DocumentationField.

## How a calculated field knows the fields on which it depends.

### `calculated_fields` vs. `formula_terms`

DocumentField has a `formula_terms` attribute, which is a
self-referential ManyToManyField whose target is DocumentField.

The `related_name` attribute of `formula_terms` is `calculated_fields`.

So if we've got:

- DocFieldNumeric1.type == 'numeric', identifier == 'A'

- DocFieldNumeric2.type == 'numeric', identifier == 'B'

- DocFieldNumeric3.type == 'numeric', identifier == 'C'

- DocFieldSum1.type == 'calculated', formula == `value = A + B`

- DocFieldSum2.type == 'calculated', formula == `value = B + C`

then we have:

- DocFieldNumeric1.calculated_fields == DocFieldSum1

- DocFieldNumeric1.calculated_fields == DocFieldSum1, DocFieldSum2

- DocFieldSum1.formula_terms == DocFieldNumeric1 and DocFieldNumeric2

- DocFieldSum1.formula_terms == DocFieldNumeric2 and DocFieldNumeric3

## When to Recalculate

### When the DocumentationField Formula Changes

All calculated field submissions related to the DocumentationField
must recalculate.

### When the Value of a Dependent Field Changes

When the value of a NumericSubmission that functions as a term in a
calculated field's formula changes,

## What to Recalculate

When the value of one of a calculated field's formula terms changes,
the calculated field should be recalculated.

Calculated fields as formula terms are also supported, though they
haven't been used in production yet.

## How to Recalculate

NumericSubmission.calculate().

### Does recalcualting save() the calculated NumericSubmission?

No. If you want to recalculate and save a NumericSubmission, call
calculate(), then save().

## When not to Recalculate?

When you're going to load DocumentationFieldSubmissions from another
source (another SubmissionSet, for example), calculating calculated
fields automatically can be problematic. If a CreditSubmission's
DocumentationFieldSubmissions are created serially, e.g., and any of
the related DocumentationFields are calculated fields, formula
calculation errors are bound to occur as formula terms are created one
at a time, and after each creation, the related calculated fields
recalculate (throwing errors until all formula terms are created).

That's the "When Not to Recalculate Use Case": during SubmissionSet
migrations.

### The `recalculate_related_calculated_fields` argument to `CreditSubmission.save()`

The `recalculate_related_calculated_fields` argument to
NumericSubmission.save() provides a way to bypass calculation of
calculated fields related to NumericSubmission.  (It defaults to
True.)

This is the hook used by the SubmissionSet migration process.
