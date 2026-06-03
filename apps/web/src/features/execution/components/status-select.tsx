import { Select } from "@/components/ui/select";
import { EXECUTION_STATUSES } from "@/types/api";

/** Inline status changer for a goal or task; emits the chosen status string. */
export function StatusSelect({
  value,
  disabled,
  onChange,
}: {
  value: string;
  disabled?: boolean;
  onChange: (status: string) => void;
}) {
  return (
    <Select
      value={value}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
      className="py-1 text-xs"
      aria-label="Status"
    >
      {EXECUTION_STATUSES.map((s) => (
        <option key={s} value={s}>
          {s.replace("_", " ")}
        </option>
      ))}
    </Select>
  );
}
