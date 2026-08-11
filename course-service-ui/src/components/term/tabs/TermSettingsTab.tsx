import { useState } from "react";
import { Card, CardTitle } from "@components/ui/Card";
import { Button } from "@components/ui/Button";

interface Props {
  courseId: string;
  termId: string;
}

export function TermSettingsTab({ termId }: Props) {
  const [displayName, setDisplayName] = useState(termId);

  return (
    <div className="grid grid-cols-[2fr_1fr] gap-6">
      <div>
        <Card>
          <CardTitle>Term Settings</CardTitle>

          <div className="mb-5">
            <label className="block text-sm font-semibold mb-2">
              Display Name
            </label>
            <input
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              className="w-full px-3 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-hbrs-dark-blue"
            />
          </div>

          <Button variant="primary">Save Settings</Button>
        </Card>
      </div>

      <div>
        <Card>
          <CardTitle>Danger Zone</CardTitle>
          <p className="text-sm text-gray-500 mb-4">
            Permanently remove this term.
          </p>
          <div className="flex flex-col gap-2">
            <Button variant="danger">Delete Term</Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
