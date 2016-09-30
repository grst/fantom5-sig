
#' merge two or more columns (i.e. samples) in an expression set
#' by applying the median over each row (i.e. feature). 
#' 
#' @param expr.set
#' @param sample.ids The column indices of the samples that 
#'    should be merged.
#' @param new.name Name of the new aggregate sample. 
#' @return new expression set 
mergeSamples = function(expr.set, sample.ids, new.name) {
  if(length(sample.ids) <= 1) {
    warning("Less than two sample ids provided. Nothing was merged.")
    return(expr.set)
  }
  # write back to data frame
  exprs(expr.set)[,sample.ids[1]] = rowMedians(exprs(expr.set)[,sample.ids])
  pData(expr.set)[sample.ids[1],]["name"] = new.name
  return(expr.set[, !(1:ncol(expr.set) %in% sample.ids[2:length(sample.ids)])])
}