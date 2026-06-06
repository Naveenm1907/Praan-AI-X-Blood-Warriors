import { Heart } from '@phosphor-icons/react';
import type { ComponentProps } from 'react';

type IconProps = ComponentProps<typeof Heart>;

export function Icon({ weight = 'regular', size = 20, ...props }: IconProps) {
  return <Heart weight={weight} size={size} {...props} />;
}

// Re-export Phosphor icons with consistent styling
export {
  Heart,
  Hospital,
  Clock,
  Phone,
  Upload,
  MagnifyingGlass,
  Funnel,
  MapPin,
  Check,
  X,
  ArrowRight,
  Brain,
  Lightning,
  Warning,
  Calendar,
  User,
  Heartbeat,
  Drop,
} from '@phosphor-icons/react';
