// Type-level checks. Don't edit.
import { Button, Card, StatusBadge } from "./ui-kit";

export const valid = (
  <>
    <Button onClick={() => {}} aria-label="Save job" type="submit" variant="danger" loading />
    <StatusBadge status="offer" />
    <Card title="Notes" actions={<Button>Add</Button>}>
      <p>Hello</p>
    </Card>
  </>
);

// @ts-expect-error — unknown variant
export const badVariant = <Button variant="link">x</Button>;
// @ts-expect-error — unknown status
export const badStatus = <StatusBadge status="ghosted" />;
// @ts-expect-error — children are required
export const noChildren = <Card title="Empty" />;
// @ts-expect-error — onClick must be a function
export const badHandler = <Button onClick="save()">x</Button>;
