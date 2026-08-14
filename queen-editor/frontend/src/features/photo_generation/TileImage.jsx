// Skeleton only -- asking the queue, drawing on a grant and releasing land in the implementation
// cycle. The signature exists so the tests next door run and fail on their assertions.
export function TileImage({ project, file, ...rest }) {
  return <img alt={file} {...rest} />;
}
