import { Check, X } from "lucide-react";
import { hasAny } from "@domain/actions";
import type { ActionText, ActionTextMap } from "@domain/actions";

interface Props<T> {
  actions: T;
  texts: ActionTextMap<T>;
  /** Also show what is not allowed, next to what is. */
  showDenied?: boolean;
}

type ActionTree = { [key: string]: boolean | ActionTree };
type GroupText = { title: string } & { [key: string]: ActionText | GroupText };

// A group whose actions all have a short label, e.g. the view/add/remove of a
// member list, is shown as one row of chips.
function isChipGroup(actions: ActionTree, texts: GroupText): boolean {
  return Object.entries(actions).every(
    ([key, value]) =>
      typeof value === "boolean" && Boolean((texts[key] as ActionText).short),
  );
}

function ActionItem({ text, granted }: { text: ActionText; granted: boolean }) {
  return (
    <li className="flex gap-2">
      {granted ? (
        <Check className="mt-0.5 size-4 shrink-0 text-green-600" />
      ) : (
        <X className="mt-0.5 size-4 shrink-0 text-gray-400" />
      )}
      <div>
        <div
          className={`text-sm font-medium ${granted ? "text-gray-900" : "text-gray-500"}`}
        >
          {text.label}
        </div>
        <div className="text-xs text-gray-500">{text.description}</div>
      </div>
    </li>
  );
}

function ChipRow({
  actions,
  texts,
  showDenied,
}: {
  actions: ActionTree;
  texts: GroupText;
  showDenied: boolean;
}) {
  const chips = Object.entries(actions).filter(
    ([, granted]) => showDenied || granted,
  );

  return (
    <li className="flex flex-wrap items-center gap-x-3 gap-y-1">
      <span className="w-40 shrink-0 text-sm text-gray-700">{texts.title}</span>
      <span className="flex flex-wrap gap-1.5">
        {chips.map(([key, granted]) => {
          const text = texts[key] as ActionText;
          return (
            <span
              key={key}
              title={text.description}
              className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                granted
                  ? "bg-green-50 text-green-700"
                  : "bg-gray-100 text-gray-400"
              }`}
            >
              {granted ? (
                <Check className="size-3" />
              ) : (
                <X className="size-3" />
              )}
              {text.short}
            </span>
          );
        })}
      </span>
    </li>
  );
}

// Renders a tree level in its order: actions as items, groups under their title.
function ActionGroup({
  actions,
  texts,
  showDenied,
}: {
  actions: ActionTree;
  texts: { [key: string]: ActionText | GroupText };
  showDenied: boolean;
}) {
  return (
    <ul className="space-y-3">
      {Object.entries(actions).map(([key, value]) => {
        if (typeof value === "boolean") {
          if (!value && !showDenied) return null;
          return (
            <ActionItem
              key={key}
              text={texts[key] as ActionText}
              granted={value}
            />
          );
        }
        if (!showDenied && !hasAny(value)) return null;
        const groupTexts = texts[key] as GroupText;
        if (isChipGroup(value, groupTexts)) {
          return (
            <ChipRow
              key={key}
              actions={value}
              texts={groupTexts}
              showDenied={showDenied}
            />
          );
        }
        return (
          <li key={key}>
            <h4 className="mb-2 text-xs font-semibold uppercase text-gray-500">
              {groupTexts.title}
            </h4>
            <div className="pl-3">
              <ActionGroup
                actions={value}
                texts={groupTexts}
                showDenied={showDenied}
              />
            </div>
          </li>
        );
      })}
    </ul>
  );
}

/** The actions of one level (LMS, course or semester), grouped like the tree. */
export function ActionList<T extends object>({
  actions,
  texts,
  showDenied = false,
}: Props<T>) {
  if (!showDenied && !hasAny(actions)) {
    return <p className="text-sm text-gray-500">Nothing at this level.</p>;
  }

  return (
    <ActionGroup
      actions={actions as unknown as ActionTree}
      texts={texts as unknown as { [key: string]: ActionText | GroupText }}
      showDenied={showDenied}
    />
  );
}
