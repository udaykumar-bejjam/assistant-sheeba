type Props = { title: string };

export function PlaceholderPage({ title }: Props) {
  return (
    <section>
      <h1>{title}</h1>
      <p className="lede">
        This module is scaffolded in the architecture. Domain ports and UI will land in the next
        implementation phases.
      </p>
    </section>
  );
}
