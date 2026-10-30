import { Link } from "react-router-dom";
import { Alert } from "@components/ui/Alert";
import { describeUnavailable, isChangeableInUi } from "@domain/unavailable";
import type { TermSummaryResponse } from "@api/types";

interface Props {
  courseId: string;
  terms: TermSummaryResponse[];
}

/** Lists the semesters whose runtime is no longer in the catalog, with what to do next. */
export function UnavailableSemestersAlert({ courseId, terms }: Props) {
  const broken = terms.filter((term) => term.unavailable.length > 0);
  if (broken.length === 0) return null;

  return (
    <Alert
      variant="warning"
      className="mb-4"
      title={`Notebook servers can't be started for ${broken.length} ${broken.length === 1 ? "semester" : "semesters"}`}
    >
      <ul className="list-disc pl-5">
        {broken.map((term) => (
          <li key={term.term_id}>
            <strong>{term.term_id}</strong>:{" "}
            {term.unavailable.map(describeUnavailable).join(" ")}{" "}
            <NextStep courseId={courseId} term={term} />
          </li>
        ))}
      </ul>
    </Alert>
  );
}

function NextStep({
  courseId,
  term,
}: {
  courseId: string;
  term: TermSummaryResponse;
}) {
  // A missing profile's description already says to contact the administrator.
  if (!term.unavailable.some(isChangeableInUi)) return null;
  if (!term.actions.environment.select) {
    return <>Please contact a course owner or instructor.</>;
  }
  return (
    <Link
      to={`/course/${courseId}/term/${term.term_id}`}
      className="font-semibold underline"
    >
      Change the Semester Runtime
    </Link>
  );
}
