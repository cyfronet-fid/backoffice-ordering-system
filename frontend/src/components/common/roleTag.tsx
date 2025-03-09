import { UserType } from "@/client";
import { Badge } from "@chakra-ui/react";

interface Props {
  role?: UserType;
}

export function RoleTag({ role }: Props) {
  const humanizedRole: Record<UserType, string> = {
    admin: "Admin",
    coordinator: "Coordinator",
    mp_user: "User",
    provider_manager: "Provider Manager",
  };

  if (role) {
    return <Badge colorScheme="blue">{humanizedRole[role]}</Badge>;
  }

  return <Badge colorScheme={"blue"}>Unknown</Badge>;
}
