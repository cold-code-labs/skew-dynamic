import { Check, Minus } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { ALL_CAPABILITIES, ROLES } from "@/config/roles"

// Read-only display of the access model from config/roles.ts. Rename labels or
// flip a capability there and this matrix follows automatically.
export function RoleMatrix() {
  return (
    <Card className="overflow-hidden p-0">
      <CardHeader className="p-4 pb-0">
        <CardTitle className="text-sm">Papéis & permissões</CardTitle>
        <CardDescription>O que cada papel pode fazer na plataforma.</CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Permissão</TableHead>
              {ROLES.map((role) => (
                <TableHead key={role.key} className="text-center">
                  {role.label}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {ALL_CAPABILITIES.map((cap) => (
              <TableRow key={cap.key}>
                <TableCell className="font-medium">{cap.label}</TableCell>
                {ROLES.map((role) => (
                  <TableCell key={role.key} className="text-center">
                    {role.capabilities.includes(cap.key) ? (
                      <Check className="mx-auto size-4 text-primary" />
                    ) : (
                      <Minus className="mx-auto size-4 text-muted-foreground/40" />
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
