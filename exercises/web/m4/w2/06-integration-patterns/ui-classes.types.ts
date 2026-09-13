// Type-level checks. Don't edit.
import { expectTypeOf } from "vitest";
import { BUTTON_SIZES, BUTTON_VARIANTS, STATUS_BADGE, badgeClasses, buttonClasses, type ButtonSize, type ButtonVariant, type Status } from "./ui-classes";

expectTypeOf<ButtonVariant>().toEqualTypeOf<"primary" | "secondary" | "danger" | "ghost">();
expectTypeOf<ButtonSize>().toEqualTypeOf<"sm" | "md" | "lg">();
expectTypeOf<keyof typeof BUTTON_VARIANTS>().toEqualTypeOf<ButtonVariant>();
expectTypeOf<keyof typeof BUTTON_SIZES>().toEqualTypeOf<ButtonSize>();
expectTypeOf<keyof typeof STATUS_BADGE>().toEqualTypeOf<Status>();
expectTypeOf(buttonClasses).returns.toEqualTypeOf<string>();

buttonClasses();
buttonClasses({ variant: "ghost", size: "lg", fullWidth: true, className: "mt-4" });
// @ts-expect-error — unknown variant
buttonClasses({ variant: "link" });
// @ts-expect-error — unknown size
buttonClasses({ size: "xl" });
// @ts-expect-error — unknown status
badgeClasses("ghosted");
