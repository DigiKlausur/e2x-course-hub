import { useState } from "react";
import { useParams } from "react-router-dom";
import { Card } from "@components/ui/Card";
import { Button } from "@components/ui/Button";
import { Alert } from "@components/ui/Alert";
import { useJoinAsStudent, useStudentJoinInfo } from "@hooks/studentJoin";
import { getErrorMessage } from "@/lib/errorMessage";
import {
  describeJoinStatus,
  describeJoined,
  joinTargetName,
} from "@domain/studentJoin";
import { config } from "@config";

const goToSpawnPage = () => window.location.assign(config.spawnUrl);

/**
 * Where a student join link leads. Joining needs a click, so link previews and
 * prefetchers that open the link do not join anyone by accident.
 */
export function JoinPage() {
  const { token = "" } = useParams<{ token: string }>();
  const { data: info, isLoading, error } = useStudentJoinInfo(token);
  const join = useJoinAsStudent(token);
  const [joined, setJoined] = useState(false);

  const handleJoin = () =>
    join.mutate(undefined, {
      onSuccess: () => {
        setJoined(true);
        if (info?.status === "open") goToSpawnPage();
      },
    });

  const canJoin = info?.status === "open" || info?.status === "not_yet_open";

  return (
    <div>
      <header className="bg-white border-b border-gray-200 px-10 py-8">
        <h1 className="text-3xl font-bold text-gray-900 m-0">
          Join a semester
        </h1>
      </header>

      <div className="px-10 py-8 max-w-lg mx-auto w-full">
        {isLoading ? (
          <p className="text-gray-500">Loading…</p>
        ) : error || !info ? (
          <Alert title="Can't join this semester">
            {getErrorMessage(error)}
          </Alert>
        ) : joined ? (
          <Card>
            <p className="text-sm">{describeJoined(info)}</p>
            {info.status === "open" && (
              <Button
                type="button"
                variant="primary"
                className="mt-4"
                onClick={goToSpawnPage}
              >
                Start a notebook server
              </Button>
            )}
          </Card>
        ) : (
          <Card>
            <h2 className="text-xl font-semibold mb-2">
              {canJoin
                ? `Join ${joinTargetName(info)} as a student?`
                : joinTargetName(info)}
            </h2>
            <p className="text-sm text-gray-500">{describeJoinStatus(info)}</p>

            {join.error && (
              <Alert className="mt-4" title="Could not join the semester">
                {getErrorMessage(join.error)}
              </Alert>
            )}

            {canJoin && (
              <Button
                type="button"
                variant="primary"
                className="mt-4"
                onClick={handleJoin}
                disabled={join.isPending}
              >
                {join.isPending ? "Joining…" : "Join"}
              </Button>
            )}
            {info.status === "already_member" && (
              <Button
                type="button"
                variant="secondary"
                className="mt-4"
                onClick={goToSpawnPage}
              >
                Start a notebook server
              </Button>
            )}
          </Card>
        )}
      </div>
    </div>
  );
}
