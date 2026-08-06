import { useState } from "react";
import { Plus } from "lucide-react";
import DepartmentForm from "../components/DepartmentForm";
import { useDepartments, useCreateDepartment } from "../hooks/useDepartments";
import type { DepartmentCreate } from "../api/departmentApi";

export default function DepartmentList() {
  const [open, setOpen] = useState(false);
  const {
    data: departments = [],
    isLoading,
    isError,
  } = useDepartments();
  const createMutation = useCreateDepartment();

  function handleSubmit(data: DepartmentCreate) {
    createMutation.mutate(data, {
      onSuccess: () => setOpen(false),
    });
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Departments</h1>
        <p>Loading departments...</p>
      </div>
    );
  }
  if (isError) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Departments</h1>
        <p className="text-red-600">
          Unable to load departments.
        </p>
      </div>
    );
  }
  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            Departments
          </h1>
          <p className="text-gray-500">
            Manage organization departments.
          </p>
        </div>
        <button
          onClick={() => setOpen(true)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          <Plus size={18} />
          Add Department
        </button>
      </div>
      <div className="overflow-hidden rounded-lg border bg-white shadow">
        <table className="min-w-full">
          <thead className="bg-slate-100">
            <tr>
              <th className="px-4 py-3 text-left">
                Code
              </th>
              <th className="px-4 py-3 text-left">
                Department Name
              </th>
              <th className="px-4 py-3 text-left">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {departments.length === 0 ? (
              <tr>
                <td
                  colSpan={3}
                  className="py-8 text-center text-gray-500"
                >
                  No departments found.
                </td>
              </tr>
            ) : (
              departments.map((department: any) => (
                <tr
                  key={department.id}
                  className="border-t"
                >
                  <td className="px-4 py-3">
                    {department.department_code}
                  </td>
                  <td className="px-4 py-3">
                    {department.department_name}
                  </td>
                  <td className="px-4 py-3">
                    {department.is_active
                      ? "Active"
                      : "Inactive"}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {open && (
        <DepartmentForm
          onSubmit={handleSubmit}
          onCancel={() => setOpen(false)}
          loading={createMutation.isPending}
        />
      )}
    </div>
  );
}
